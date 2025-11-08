#!/usr/bin/env python3
"""
Simplified Transliterator wrapper for fairseq
Adapted from fairseq's interactive translation
"""

import ast
import math
import os
import time
from argparse import Namespace
from collections import namedtuple

import numpy as np
import torch

from fairseq import checkpoint_utils, options, tasks, utils
from fairseq.dataclass.utils import convert_namespace_to_omegaconf
from fairseq.token_generation_constraints import pack_constraints, unpack_constraints
from fairseq_cli.generate import get_symbols_to_strip_from_output

Batch = namedtuple("Batch", "ids src_tokens src_lengths constraints")


def make_batches(lines, cfg, task, max_positions, encode_fn):
    """Create batches from input lines"""
    
    if cfg.generation.constraints:
        batch_constraints = [list() for _ in lines]
        for i, line in enumerate(lines):
            if "\t" in line:
                lines[i], *batch_constraints[i] = line.split("\t")
        
        for i, constraint_list in enumerate(batch_constraints):
            batch_constraints[i] = [
                task.target_dictionary.encode_line(
                    encode_fn(constraint),
                    append_eos=False,
                    add_if_not_exist=False,
                )
                for constraint in constraint_list
            ]
        
        constraints_tensor = pack_constraints(batch_constraints)
    else:
        constraints_tensor = None
    
    tokens, lengths = task.get_interactive_tokens_and_lengths(lines, encode_fn)
    
    itr = task.get_batch_iterator(
        dataset=task.build_dataset_for_inference(
            tokens, lengths, constraints=constraints_tensor
        ),
        max_tokens=cfg.dataset.max_tokens,
        max_sentences=cfg.dataset.batch_size,
        max_positions=max_positions,
        ignore_invalid_inputs=cfg.dataset.skip_invalid_size_inputs_valid_test,
    ).next_epoch_itr(shuffle=False)
    
    for batch in itr:
        yield Batch(
            ids=batch["id"],
            src_tokens=batch["net_input"]["src_tokens"],
            src_lengths=batch["net_input"]["src_lengths"],
            constraints=batch.get("constraints", None),
        )


class Transliterator:
    """
    Simplified transliterator for Gujarati
    """
    
    def __init__(self, data_bin_dir, model_checkpoint_path, lang_pairs_csv, 
                 lang_list_file, beam, batch_size=32):
        """
        Initialize transliterator
        
        Args:
            data_bin_dir: Path to binarized data directory
            model_checkpoint_path: Path to model checkpoint
            lang_pairs_csv: Language pairs (e.g., "en-gu" or "gu-en")
            lang_list_file: Path to language list file
            beam: Beam search width
            batch_size: Batch size for inference
        """
        
        self.parser = options.get_interactive_generation_parser()
        
        self.parser.set_defaults(
            path=model_checkpoint_path,
            num_workers=-1,
            batch_size=batch_size,
            buffer_size=batch_size + 1,
            task="translation_multi_simple_epoch",
            beam=beam,
        )
        
        self.args = options.parse_args_and_arch(self.parser, input_args=[data_bin_dir])
        
        self.args.skip_invalid_size_inputs_valid_test = False
        self.args.lang_pairs = lang_pairs_csv
        self.args.lang_dict = lang_list_file
        
        self.cfg = convert_namespace_to_omegaconf(self.args)
        
        if isinstance(self.cfg, Namespace):
            self.cfg = convert_namespace_to_omegaconf(self.cfg)
        
        self.total_translate_time = 0
        
        utils.import_user_module(self.cfg.common)
        
        if self.cfg.interactive.buffer_size < 1:
            self.cfg.interactive.buffer_size = 1
        if self.cfg.dataset.max_tokens is None and self.cfg.dataset.batch_size is None:
            self.cfg.dataset.batch_size = 1
        
        assert (
            not self.cfg.generation.sampling or 
            self.cfg.generation.nbest == self.cfg.generation.beam
        ), "--sampling requires --nbest to be equal to --beam"
        
        assert (
            not self.cfg.dataset.batch_size or 
            self.cfg.dataset.batch_size <= self.cfg.interactive.buffer_size
        ), "--batch-size cannot be larger than --buffer-size"
        
        self.use_cuda = torch.cuda.is_available() and not self.cfg.common.cpu
        
        # Setup task
        self.task = tasks.setup_task(self.cfg.task)
        
        # Load model ensemble
        overrides = ast.literal_eval(self.cfg.common_eval.model_overrides)
        self.models, _model_args = checkpoint_utils.load_model_ensemble(
            utils.split_paths(self.cfg.common_eval.path),
            arg_overrides=overrides,
            task=self.task,
            suffix=self.cfg.checkpoint.checkpoint_suffix,
            strict=(self.cfg.checkpoint.checkpoint_shard_count == 1),
            num_shards=self.cfg.checkpoint.checkpoint_shard_count,
        )
        
        # Set dictionaries
        self.src_dict = self.task.source_dictionary
        self.tgt_dict = self.task.target_dictionary
        
        # Optimize models for generation
        for i in range(len(self.models)):
            if self.models[i] is None:
                continue
            if self.cfg.common.fp16:
                self.models[i].half()
            if self.use_cuda and not self.cfg.distributed_training.pipeline_model_parallel:
                self.models[i].cuda()
            self.models[i].prepare_for_inference_(self.cfg)
        
        # Initialize generator
        self.generator = self.task.build_generator(self.models, self.cfg.generation)
        
        # Handle tokenization and BPE
        self.tokenizer = self.task.build_tokenizer(self.cfg.tokenizer)
        self.bpe = self.task.build_bpe(self.cfg.bpe)
        
        # Load alignment dictionary
        self.align_dict = utils.load_align_dict(self.cfg.generation.replace_unk)
        
        self.max_positions = utils.resolve_max_positions(
            self.task.max_positions(), 
            *[model.max_positions() for model in self.models]
        )
    
    def encode_fn(self, x):
        """Encode input text"""
        if self.tokenizer is not None:
            x = self.tokenizer.encode(x)
        if self.bpe is not None:
            x = self.bpe.encode(x)
        return x
    
    def decode_fn(self, x):
        """Decode output text"""
        if self.bpe is not None:
            x = self.bpe.decode(x)
        if self.tokenizer is not None:
            x = self.tokenizer.decode(x)
        return x
    
    def translate(self, inputs, nbest=1):
        """
        Translate input texts
        
        Args:
            inputs: List of input strings
            nbest: Number of best hypotheses to return
            
        Returns:
            Formatted string with translation results
        """
        start_id = 0
        results = []
        
        for batch in make_batches(inputs, self.cfg, self.task, self.max_positions, self.encode_fn):
            bsz = batch.src_tokens.size(0)
            src_tokens = batch.src_tokens
            src_lengths = batch.src_lengths
            constraints = batch.constraints
            
            if self.use_cuda:
                src_tokens = src_tokens.cuda()
                src_lengths = src_lengths.cuda()
                if constraints is not None:
                    constraints = constraints.cuda()
            
            sample = {
                "net_input": {
                    "src_tokens": src_tokens,
                    "src_lengths": src_lengths,
                },
            }
            
            translate_start_time = time.time()
            translations = self.task.inference_step(
                self.generator, self.models, sample, constraints=constraints
            )
            translate_time = time.time() - translate_start_time
            self.total_translate_time += translate_time
            
            list_constraints = [[] for _ in range(bsz)]
            if self.cfg.generation.constraints:
                list_constraints = [unpack_constraints(c) for c in constraints]
            
            for i, (id, hypos) in enumerate(zip(batch.ids.tolist(), translations)):
                src_tokens_i = utils.strip_pad(src_tokens[i], self.tgt_dict.pad())
                constraints = list_constraints[i]
                results.append((
                    start_id + id,
                    src_tokens_i,
                    hypos,
                    {
                        "constraints": constraints,
                        "time": translate_time / len(translations),
                    },
                ))
        
        # Format output
        result_str = ""
        for id_, src_tokens, hypos, info in sorted(results, key=lambda x: x[0]):
            src_str = ""
            if self.src_dict is not None:
                src_str = self.src_dict.string(src_tokens, self.cfg.common_eval.post_process)
                result_str += "S-{}\t{}".format(id_, src_str) + '\n'
                result_str += "W-{}\t{:.3f}\tseconds".format(id_, info["time"]) + '\n'
                
                for constraint in info["constraints"]:
                    result_str += "C-{}\t{}".format(
                        id_,
                        self.tgt_dict.string(constraint, self.cfg.common_eval.post_process),
                    ) + '\n'
            
            # Process top predictions
            for hypo in hypos[:min(len(hypos), nbest)]:
                hypo_tokens, hypo_str, alignment = utils.post_process_prediction(
                    hypo_tokens=hypo["tokens"].int().cpu(),
                    src_str=src_str,
                    alignment=hypo["alignment"],
                    align_dict=self.align_dict,
                    tgt_dict=self.tgt_dict,
                    remove_bpe=self.cfg.common_eval.post_process,
                    extra_symbols_to_ignore=get_symbols_to_strip_from_output(self.generator),
                )
                detok_hypo_str = self.decode_fn(hypo_str)
                score = hypo["score"] / math.log(2)
                
                result_str += "H-{}\t{}\t{}".format(id_, score, hypo_str) + '\n'
                result_str += "D-{}\t{}\t{}".format(id_, score, detok_hypo_str) + '\n'
                result_str += "P-{}\t{}".format(
                    id_,
                    " ".join(
                        map(
                            lambda x: "{:.4f}".format(x),
                            hypo["positional_scores"].div_(math.log(2)).tolist(),
                        )
                    ),
                ) + '\n'
                
                if self.cfg.generation.print_alignment:
                    alignment_str = " ".join(
                        ["{}-{}".format(src, tgt) for src, tgt in alignment]
                    )
                    result_str += "A-{}\t{}".format(id_, alignment_str) + '\n'
        
        return result_str
