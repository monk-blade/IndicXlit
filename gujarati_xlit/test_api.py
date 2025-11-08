#!/usr/bin/env python3
"""
Test script for Gujarati Transliteration Server
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("\n" + "="*60)
    print("Testing Health Endpoint")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

def test_en2gu_word():
    """Test Roman to Gujarati word transliteration"""
    print("\n" + "="*60)
    print("Testing Roman → Gujarati (Word)")
    print("="*60)
    
    test_words = ["namaste", "Gujarat", "bharat", "duniya"]
    
    for word in test_words:
        response = requests.get(f"{BASE_URL}/tl/gu/{word}?num_suggestions=3")
        data = response.json()
        print(f"\nInput: {word}")
        print(f"Output: {', '.join(data['result'])}")

def test_gu2en_word():
    """Test Gujarati to Roman word romanization"""
    print("\n" + "="*60)
    print("Testing Gujarati → Roman (Word)")
    print("="*60)
    
    test_words = ["નમસ્તે", "ગુજરાત", "ભારત", "દુનિયા"]
    
    for word in test_words:
        response = requests.get(f"{BASE_URL}/rtl/gu/{word}?num_suggestions=3")
        data = response.json()
        print(f"\nInput: {word}")
        print(f"Output: {', '.join(data['result'])}")

def test_en2gu_sentence():
    """Test Roman to Gujarati sentence transliteration"""
    print("\n" + "="*60)
    print("Testing Roman → Gujarati (Sentence)")
    print("="*60)
    
    test_sentences = [
        "namaste duniya",
        "mane Gujarat gamche",
        "Bharat ek sundar desh che"
    ]
    
    for sentence in test_sentences:
        response = requests.post(
            f"{BASE_URL}/sentence/en2gu",
            json={"text": sentence}
        )
        data = response.json()
        print(f"\nInput: {sentence}")
        print(f"Output: {data['result']}")

def test_gu2en_sentence():
    """Test Gujarati to Roman sentence romanization"""
    print("\n" + "="*60)
    print("Testing Gujarati → Roman (Sentence)")
    print("="*60)
    
    test_sentences = [
        "નમસ્તે દુનિયા",
        "મને ગુજરાત ગમે છે",
        "ભારત એક સુંદર દેશ છે"
    ]
    
    for sentence in test_sentences:
        response = requests.post(
            f"{BASE_URL}/sentence/gu2en",
            json={"text": sentence}
        )
        data = response.json()
        print(f"\nInput: {sentence}")
        print(f"Output: {data['result']}")

def main():
    print("\n" + "="*60)
    print("Gujarati Transliteration Server - Test Suite")
    print("="*60)
    print(f"Testing server at: {BASE_URL}")
    
    try:
        # Run all tests
        test_health()
        test_en2gu_word()
        test_gu2en_word()
        test_en2gu_sentence()
        test_gu2en_sentence()
        
        print("\n" + "="*60)
        print("✓ All tests completed successfully!")
        print("="*60 + "\n")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to server")
        print(f"Please ensure the server is running at {BASE_URL}")
        print("Start the server with: python server.py")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    main()
