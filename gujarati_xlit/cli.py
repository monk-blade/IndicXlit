#!/usr/bin/env python3
"""
Simple command-line interface for Gujarati transliteration
"""

import sys
from xlit_engine import GujaratiXlitEngine

def print_banner():
    print("\n" + "="*60)
    print("Gujarati Transliteration CLI")
    print("="*60 + "\n")

def main():
    if len(sys.argv) < 3:
        print("Usage:")
        print("  python cli.py <direction> <text>")
        print("\nDirections:")
        print("  en2gu  - Roman to Gujarati")
        print("  gu2en  - Gujarati to Roman")
        print("\nExamples:")
        print("  python cli.py en2gu namaste")
        print('  python cli.py gu2en "નમસ્તે"')
        sys.exit(1)
    
    direction = sys.argv[1]
    text = " ".join(sys.argv[2:])
    
    if direction not in ['en2gu', 'gu2en']:
        print(f"Error: Invalid direction '{direction}'")
        print("Use 'en2gu' or 'gu2en'")
        sys.exit(1)
    
    print_banner()
    print(f"Direction: {direction}")
    print(f"Input: {text}\n")
    
    # Initialize engine
    print("Loading transliteration model...")
    engine = GujaratiXlitEngine(direction=direction, beam_width=4, rescore=True)
    
    # Check if input is a sentence or word
    if ' ' in text:
        print("\nTransliterating sentence...")
        result = engine.translit_sentence(text)
        print(f"Result: {result}")
    else:
        print("\nTop 5 suggestions:")
        results = engine.translit_word(text, topk=5)
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result}")
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
