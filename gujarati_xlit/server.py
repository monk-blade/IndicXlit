#!/usr/bin/env python3
"""
Minimal Gujarati Transliteration Server
Provides REST API for Roman <-> Gujarati transliteration
"""

from flask import Flask, jsonify, request, make_response
from datetime import datetime
import traceback

# Import Gujarati transliteration engine
from xlit_engine import GujaratiXlitEngine

# Initialize Flask app
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# Initialize both engines (lazy loading)
ENGINES = {}

def get_engine(direction):
    """Get or initialize engine for given direction"""
    if direction not in ENGINES:
        print(f"Initializing {direction} engine...")
        ENGINES[direction] = GujaratiXlitEngine(direction=direction, beam_width=4, rescore=True)
    return ENGINES[direction]


@app.route('/', methods=['GET'])
def home():
    """Home endpoint with API documentation"""
    return jsonify({
        'service': 'Gujarati Transliteration API',
        'version': '1.0.0',
        'endpoints': {
            '/': 'This help page',
            '/health': 'Health check endpoint',
            '/tl/gu/<word>': 'Roman to Gujarati transliteration',
            '/rtl/gu/<word>': 'Gujarati to Roman transliteration (romanization)',
            '/sentence/en2gu': 'POST endpoint for sentence transliteration (roman to gujarati)',
            '/sentence/gu2en': 'POST endpoint for sentence romanization (gujarati to roman)',
        },
        'examples': {
            'word_en2gu': '/tl/gu/namaste',
            'word_gu2en': '/rtl/gu/નમસ્તે',
            'sentence_en2gu': 'POST /sentence/en2gu with body: {"text": "namaste duniya"}',
            'sentence_gu2en': 'POST /sentence/gu2en with body: {"text": "નમસ્તે દુનિયા"}',
        }
    })


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'gujarati-xlit',
        'timestamp': str(datetime.utcnow()) + ' UTC',
        'engines_loaded': list(ENGINES.keys())
    })


@app.route('/tl/gu/<word>', methods=['GET'])
def transliterate_en2gu(word):
    """
    Transliterate from Roman script to Gujarati
    
    Example: /tl/gu/namaste
    Query params:
        - num_suggestions: Number of suggestions to return (default: 5)
    """
    response = {
        'success': False,
        'error': '',
        'at': str(datetime.utcnow()) + ' UTC',
        'input': word.strip(),
        'result': []
    }
    
    try:
        num_suggestions = request.args.get('num_suggestions', default=5, type=int)
        num_suggestions = min(max(num_suggestions, 1), 10)  # Clamp between 1-10
        
        engine = get_engine('en2gu')
        results = engine.translit_word(word, topk=num_suggestions)
        
        response['result'] = results
        response['success'] = True
        
    except Exception as e:
        response['error'] = f'Internal error: {str(e)}'
        print("Error in en2gu:", traceback.format_exc())
    
    return jsonify(response)


@app.route('/rtl/gu/<word>', methods=['GET'])
def transliterate_gu2en(word):
    """
    Romanize Gujarati text to Roman script
    
    Example: /rtl/gu/નમસ્તે
    Query params:
        - num_suggestions: Number of suggestions to return (default: 5)
    """
    response = {
        'success': False,
        'error': '',
        'at': str(datetime.utcnow()) + ' UTC',
        'input': word.strip(),
        'result': []
    }
    
    try:
        num_suggestions = request.args.get('num_suggestions', default=5, type=int)
        num_suggestions = min(max(num_suggestions, 1), 10)  # Clamp between 1-10
        
        engine = get_engine('gu2en')
        results = engine.translit_word(word, topk=num_suggestions)
        
        response['result'] = results
        response['success'] = True
        
    except Exception as e:
        response['error'] = f'Internal error: {str(e)}'
        print("Error in gu2en:", traceback.format_exc())
    
    return jsonify(response)


@app.route('/sentence/en2gu', methods=['POST'])
def sentence_en2gu():
    """
    Transliterate sentence from Roman to Gujarati
    
    POST body: {"text": "namaste duniya"}
    Returns: {"result": "નમસ્તે દુનિયા", ...}
    """
    response = {
        'success': False,
        'error': '',
        'at': str(datetime.utcnow()) + ' UTC',
        'input': '',
        'result': ''
    }
    
    try:
        data = request.get_json(force=True)
        if 'text' not in data:
            response['error'] = 'Missing "text" field in request body'
            return jsonify(response), 400
        
        text = data['text'].strip()
        response['input'] = text
        
        engine = get_engine('en2gu')
        result = engine.translit_sentence(text)
        
        response['result'] = result
        response['success'] = True
        
    except Exception as e:
        response['error'] = f'Internal error: {str(e)}'
        print("Error in sentence en2gu:", traceback.format_exc())
        return jsonify(response), 500
    
    return jsonify(response)


@app.route('/sentence/gu2en', methods=['POST'])
def sentence_gu2en():
    """
    Romanize Gujarati sentence to Roman script
    
    POST body: {"text": "નમસ્તે દુનિયા"}
    Returns: {"result": "namaste duniya", ...}
    """
    response = {
        'success': False,
        'error': '',
        'at': str(datetime.utcnow()) + ' UTC',
        'input': '',
        'result': ''
    }
    
    try:
        data = request.get_json(force=True)
        if 'text' not in data:
            response['error'] = 'Missing "text" field in request body'
            return jsonify(response), 400
        
        text = data['text'].strip()
        response['input'] = text
        
        engine = get_engine('gu2en')
        result = engine.translit_sentence(text)
        
        response['result'] = result
        response['success'] = True
        
    except Exception as e:
        response['error'] = f'Internal error: {str(e)}'
        print("Error in sentence gu2en:", traceback.format_exc())
        return jsonify(response), 500
    
    return jsonify(response)


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Endpoint not found',
        'message': 'Please check the API documentation at /',
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'error': 'Internal server error',
        'message': 'Something went wrong. Please try again later.',
    }), 500


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Gujarati Transliteration Server')
    parser.add_argument('--host', type=str, default='0.0.0.0', 
                       help='Host to bind to (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=8000, 
                       help='Port to bind to (default: 8000)')
    parser.add_argument('--debug', action='store_true', 
                       help='Run in debug mode')
    parser.add_argument('--preload', choices=['en2gu', 'gu2en', 'both'], default=None,
                       help='Preload engines at startup (default: lazy loading)')
    
    args = parser.parse_args()
    
    # Preload engines if requested
    if args.preload:
        print("Preloading engines...")
        if args.preload in ['en2gu', 'both']:
            get_engine('en2gu')
        if args.preload in ['gu2en', 'both']:
            get_engine('gu2en')
        print("✓ All requested engines loaded!")
    
    print(f"\n{'='*60}")
    print(f"🚀 Gujarati Transliteration Server Starting")
    print(f"{'='*60}")
    print(f"Host: {args.host}")
    print(f"Port: {args.port}")
    print(f"Debug: {args.debug}")
    print(f"{'='*60}\n")
    print(f"API Documentation: http://{args.host}:{args.port}/")
    print(f"Health Check: http://{args.host}:{args.port}/health")
    print(f"\nExample requests:")
    print(f"  curl http://{args.host}:{args.port}/tl/gu/namaste")
    print(f"  curl http://{args.host}:{args.port}/rtl/gu/નમસ્તે")
    print(f"\n{'='*60}\n")
    
    app.run(
        host=args.host,
        port=args.port,
        debug=args.debug,
        threaded=True
    )
