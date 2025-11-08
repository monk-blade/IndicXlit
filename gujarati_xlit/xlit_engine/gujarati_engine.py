"""
Gujarati-only Transliteration Engine
Simplified version for roman<->gujarati transliteration only
"""
import os
import re
import ujson
from pydload import dload
import zipfile
import tqdm
from indicnlp.normalize.indic_normalize import IndicNormalizerFactory

# Constants
MODEL_FILE = 'transformer/indicxlit.pt'
DICTS_FOLDER = 'word_prob_dicts'
CHARS_FOLDER = 'corpus-bin'
DICT_FILE_FORMAT = '%s_word_prob_dict.json'
LANG_LIST_FILE = 'lang_list.txt'

# Gujarati-specific constants
GUJARATI_CODE = 'gu'
GUJARATI_UNICODE_RANGE = '\u0A80-\u0AFF'
GUJARATI_REGEX = re.compile(f"[{GUJARATI_UNICODE_RANGE}]+")

# Model URLs
EN2INDIC_MODEL_URL = 'https://github.com/AI4Bharat/IndicXlit/releases/download/v1.0/indicxlit-en-indic-v1.0.zip'
INDIC2EN_MODEL_URL = 'https://github.com/AI4Bharat/IndicXlit/releases/download/v1.0/indicxlit-indic-en-v1.0.zip'
EN2INDIC_DICTS_URL = 'https://github.com/AI4Bharat/IndicXlit/releases/download/v1.0/word_prob_dicts.zip'
INDIC2EN_DICTS_URL = 'https://github.com/AI4Bharat/IndicXlit/releases/download/v1.0/word_prob_dicts_en.zip'

XLIT_VERSION = "v1.0"

normalizer_factory = IndicNormalizerFactory()


class GujaratiXlitEngine:
    """
    Minimal Gujarati Transliteration Engine
    Supports both roman->gujarati and gujarati->roman
    """
    
    def __init__(self, direction="en2gu", beam_width=4, rescore=True):
        """
        Initialize Gujarati transliteration engine
        
        Args:
            direction: "en2gu" for roman->gujarati, "gu2en" for gujarati->roman
            beam_width: Beam search width (default: 4)
            rescore: Use dictionary-based rescoring (default: True)
        """
        self.direction = direction
        self.beam_width = beam_width
        self._rescore = rescore
        
        # Determine model paths based on direction
        if direction == "en2gu":
            self.src_script = "roman"
            self.tgt_script = "gujarati"
            model_url = EN2INDIC_MODEL_URL
            dicts_url = EN2INDIC_DICTS_URL
            lang_pair = "en-gu"
        else:  # gu2en
            self.src_script = "gujarati"
            self.tgt_script = "roman"
            model_url = INDIC2EN_MODEL_URL
            dicts_url = INDIC2EN_DICTS_URL
            lang_pair = "gu-en"
        
        # Setup model directory
        models_path = self._get_models_path(direction)
        os.makedirs(models_path, exist_ok=True)
        
        # Download models if needed
        self._download_models(models_path, model_url)
        
        # Download dictionaries if rescoring is enabled
        if self._rescore:
            self._download_dicts(models_path, dicts_url)
            # Load word probability dictionary
            dicts_folder = os.path.join(models_path, DICTS_FOLDER)
            dict_file = os.path.join(dicts_folder, DICT_FILE_FORMAT % GUJARATI_CODE)
            if os.path.exists(dict_file):
                print(f"Loading Gujarati dictionary for rescoring...")
                self.word_prob_dict = ujson.load(open(dict_file))
            else:
                print(f"Warning: Dictionary file not found at {dict_file}, disabling rescoring")
                self._rescore = False
                self.word_prob_dict = {}
        else:
            self.word_prob_dict = {}
        
        # Initialize transliterator
        print("Initializing Gujarati transliteration model...")
        from .transliterator import Transliterator
        self.transliterator = Transliterator(
            os.path.join(models_path, CHARS_FOLDER),
            os.path.join(models_path, MODEL_FILE),
            lang_pairs_csv=lang_pair,
            lang_list_file=os.path.join(models_path, LANG_LIST_FILE),
            beam=beam_width,
            batch_size=32,
        )
        
        print("✓ Gujarati transliteration engine initialized successfully!")
    
    def _get_models_path(self, direction):
        """Get or create models directory"""
        script_dir = os.path.dirname(os.path.realpath(__file__))
        
        if os.access(script_dir, os.W_OK | os.X_OK):
            models_path = os.path.join(script_dir, 'models')
        else:
            user_home = os.path.expanduser("~")
            models_path = os.path.join(user_home, '.gujarati_xlit_models')
        
        model_dir = "en2indic" if direction == "en2gu" else "indic2en"
        return os.path.join(models_path, model_dir, XLIT_VERSION)
    
    def _download_models(self, models_path, download_url):
        """Download transliteration model if not present"""
        model_file_path = os.path.join(models_path, MODEL_FILE)
        chars_folder = os.path.join(models_path, CHARS_FOLDER)
        
        if not os.path.isfile(model_file_path) or not os.path.isdir(chars_folder):
            print(f'Downloading transliteration model (contains all languages)...')
            downloaded_zip_path = os.path.join(models_path, 'model.zip')
            
            dload(url=download_url, save_to_path=downloaded_zip_path, max_time=None)
            
            if not os.path.isfile(downloaded_zip_path):
                raise Exception(f'ERROR: Unable to download model from {download_url}')
            
            print('Extracting model files...')
            with zipfile.ZipFile(downloaded_zip_path, 'r') as zip_ref:
                zip_ref.extractall(models_path)
            
            # Remove zip file
            if os.path.isfile(model_file_path):
                os.remove(downloaded_zip_path)
                print(f"✓ Model extracted to: {models_path}")
                
                # Clean up: remove unnecessary language-specific files from corpus-bin if they exist
                # Keep only Gujarati and English related files
                if os.path.isdir(chars_folder):
                    print('Optimizing: keeping only Gujarati-related files...')
                    # Most multilingual models share weights, so we keep the main structure
                    # Only dictionary files in corpus-bin might have per-language data
                    # For now, we keep everything as the model file itself is shared
                    pass
            else:
                raise Exception(f'ERROR: Model file not found after extraction')
        
        # Ensure lang_list.txt exists with only en and gu
        lang_list_path = os.path.join(models_path, LANG_LIST_FILE)
        if not os.path.isfile(lang_list_path):
            print("Creating lang_list.txt file with only en and gu...")
            with open(lang_list_path, 'w') as f:
                f.write('en\ngu\n')
            print(f"✓ Created {lang_list_path}")
        else:
            # Check if it has only en and gu, if not, update it
            with open(lang_list_path, 'r') as f:
                langs = f.read().strip().split('\n')
            if set(langs) != {'en', 'gu'}:
                print("Updating lang_list.txt to contain only en and gu...")
                with open(lang_list_path, 'w') as f:
                    f.write('en\ngu\n')
                print(f"✓ Updated {lang_list_path}")
    
    def _download_dicts(self, models_path, download_url):
        """Download dictionary for rescoring if not present"""
        dicts_folder = os.path.join(models_path, DICTS_FOLDER)
        gujarati_dict_file = os.path.join(dicts_folder, DICT_FILE_FORMAT % GUJARATI_CODE)
        
        if not os.path.isfile(gujarati_dict_file):
            print('Downloading dictionaries (contains all languages)...')
            downloaded_zip_path = os.path.join(models_path, 'dicts.zip')
            
            dload(url=download_url, save_to_path=downloaded_zip_path, max_time=None)
            
            if not os.path.isfile(downloaded_zip_path):
                raise Exception(f'ERROR: Unable to download dictionaries from {download_url}')
            
            # Extract all dictionaries temporarily
            print('Extracting dictionaries...')
            with zipfile.ZipFile(downloaded_zip_path, 'r') as zip_ref:
                zip_ref.extractall(models_path)
            
            # Remove the zip file
            os.remove(downloaded_zip_path)
            
            # Keep only Gujarati dictionary, remove others
            if os.path.isdir(dicts_folder):
                print('Keeping only Gujarati dictionary, removing other languages...')
                dict_files = os.listdir(dicts_folder)
                for dict_file in dict_files:
                    if dict_file != (DICT_FILE_FORMAT % GUJARATI_CODE):
                        file_path = os.path.join(dicts_folder, dict_file)
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                            print(f'  Removed: {dict_file}')
                
                if os.path.isfile(gujarati_dict_file):
                    print(f"✓ Gujarati dictionary ready at: {gujarati_dict_file}")
                else:
                    print(f"Warning: Gujarati dictionary not found after extraction")
            else:
                raise Exception(f'ERROR: Dictionaries folder not found after extraction')
    
    def _normalize_gujarati(self, words):
        """Normalize Gujarati text"""
        normalizer = normalizer_factory.get_normalizer(GUJARATI_CODE)
        return [normalizer.normalize(word) for word in words]
    
    def _pre_process(self, words):
        """Pre-process words for transliteration"""
        if self.src_script == "gujarati":
            words = self._normalize_gujarati(words)
        
        # Convert word to space-separated characters
        words = [' '.join(list(word.lower())) for word in words]
        
        # Add language token
        words = ['__gu__ ' + word for word in words]
        
        return words
    
    def _rescore_results(self, res_dict, result_dict, alpha=0.9):
        """Rescore results using word probability dictionary"""
        output_data = {}
        
        for src_word_id in res_dict.keys():
            src_word = res_dict[src_word_id]['S']
            candidates = [h[0] for h in res_dict[src_word_id]['H']]
            
            # Remove spaces from candidates
            candidates_no_space = [''.join(c.split(' ')) for c in candidates]
            
            # Calculate normalized probabilities
            total_model_score = sum(result_dict[src_word].get(c, 0) for c in candidates)
            total_dict_prob = sum(self.word_prob_dict.get(c, 0) for c in candidates_no_space)
            
            # Combine scores
            scored_candidates = []
            for orig_candidate, clean_candidate in zip(candidates, candidates_no_space):
                model_score = result_dict[src_word].get(orig_candidate, 0) / max(total_model_score, 1e-10)
                dict_prob = self.word_prob_dict.get(clean_candidate, 0) / max(total_dict_prob, 1e-10)
                
                combined_score = alpha * model_score + (1 - alpha) * dict_prob
                scored_candidates.append((clean_candidate, combined_score))
            
            # Sort by combined score
            scored_candidates.sort(key=lambda x: x[1], reverse=True)
            output_data[src_word] = [c[0] for c in scored_candidates]
        
        return output_data
    
    def _post_process(self, translation_str):
        """Post-process model output to extract transliterations"""
        lines = translation_str.split('\n')
        
        list_s = [line for line in lines if 'S-' in line]
        list_h = [line for line in lines if 'H-' in line]
        
        list_s.sort(key=lambda x: int(x.split('\t')[0].split('-')[1]))
        list_h.sort(key=lambda x: int(x.split('\t')[0].split('-')[1]))
        
        # Build result dictionary
        res_dict = {}
        for s in list_s:
            s_id = int(s.split('\t')[0].split('-')[1])
            res_dict[s_id] = {'S': s.split('\t')[1], 'H': []}
            
            for h in list_h:
                h_id = int(h.split('\t')[0].split('-')[1])
                if s_id == h_id:
                    score = pow(2, float(h.split('\t')[1]))
                    res_dict[s_id]['H'].append((h.split('\t')[2], score))
            
            res_dict[s_id]['H'].sort(key=lambda x: float(x[1]), reverse=True)
        
        # Build result dict for rescoring
        result_dict = {}
        for i in res_dict.keys():
            result_dict[res_dict[i]['S']] = {
                res_dict[i]['H'][j][0]: res_dict[i]['H'][j][1]
                for j in range(len(res_dict[i]['H']))
            }
        
        # Apply rescoring if enabled
        transliterated_words = []
        if self._rescore and self.word_prob_dict:
            output_dict = self._rescore_results(res_dict, result_dict)
            for src_word in output_dict.keys():
                transliterated_words.extend(output_dict[src_word])
        else:
            for i in res_dict.keys():
                transliterated_words.extend([h[0] for h in res_dict[i]['H']])
        
        # Remove extra spaces
        transliterated_words = [''.join(word.split(' ')) for word in transliterated_words]
        
        return transliterated_words
    
    def translit_word(self, word, topk=5):
        """
        Transliterate a single word
        
        Args:
            word: Input word (roman for en2gu, gujarati for gu2en)
            topk: Number of top suggestions to return
            
        Returns:
            List of transliterated suggestions
        """
        if not word or not word.strip():
            return []
        
        word = word.strip()
        
        # Pre-process
        processed = self._pre_process([word])
        
        # Transliterate
        output_str = self.transliterator.translate(processed)
        
        # Post-process
        results = self._post_process(output_str)
        
        # Return top-k results
        return results[:topk]
    
    def translit_sentence(self, sentence):
        """
        Transliterate a sentence (returns top-1 for each word)
        
        Args:
            sentence: Input sentence
            
        Returns:
            Transliterated sentence
        """
        if not sentence or not sentence.strip():
            return ""
        
        words = sentence.strip().split()
        transliterated = []
        
        for word in words:
            results = self.translit_word(word, topk=1)
            if results:
                transliterated.append(results[0])
            else:
                transliterated.append(word)
        
        return ' '.join(transliterated)
