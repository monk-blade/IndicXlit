# Gujarati Transliteration Server

A minimal, portable REST API server for **Gujarati transliteration** supporting both:
- **Roman → Gujarati** (English script to Gujarati script)
- **Gujarati → Roman** (Gujarati script to English script / Romanization)

This is a lightweight, standalone version extracted from the [IndicXlit](https://github.com/AI4Bharat/IndicXlit) project, optimized for Gujarati language only.

## Features

✨ **Minimal & Fast**: Only Gujarati support, no multi-language overhead  
🐳 **Docker Ready**: Easy deployment with Docker  
🔄 **Bi-directional**: Both Roman↔Gujarati transliteration  
📦 **Portable**: Self-contained package with automatic model download  
🎯 **Simple API**: RESTful endpoints with JSON responses  

## Quick Start

### Option 1: Docker (Recommended)

```bash
# Build the Docker image
docker build -t gujarati-xlit .

# Run the container
docker run -p 8000:8000 gujarati-xlit

# Access the API
curl http://localhost:8000/tl/gu/namaste
```

### Option 2: Direct Python

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python server.py

# Or with custom options
python server.py --host 0.0.0.0 --port 8000 --preload both
```

**First Run**: Models (~150MB) will be automatically downloaded from GitHub on first use.

## API Endpoints

### 1. Health Check
```bash
GET /health
```
Response:
```json
{
  "status": "healthy",
  "service": "gujarati-xlit",
  "timestamp": "2025-11-08 12:00:00 UTC",
  "engines_loaded": ["en2gu"]
}
```

### 2. Roman → Gujarati (Word)
```bash
GET /tl/gu/<word>?num_suggestions=5
```

Example:
```bash
curl "http://localhost:8000/tl/gu/namaste?num_suggestions=5"
```

Response:
```json
{
  "success": true,
  "error": "",
  "at": "2025-11-08 12:00:00 UTC",
  "input": "namaste",
  "result": ["નમસ્તે", "નમસ્ટે", "નમાસ્તે", "નમસ્તેં", "નમસતે"]
}
```

### 3. Gujarati → Roman (Word)
```bash
GET /rtl/gu/<word>?num_suggestions=5
```

Example:
```bash
curl "http://localhost:8000/rtl/gu/નમસ્તે?num_suggestions=5"
```

Response:
```json
{
  "success": true,
  "error": "",
  "at": "2025-11-08 12:00:00 UTC",
  "input": "નમસ્તે",
  "result": ["namaste", "namastey", "namasthe", "namastay", "namste"]
}
```

### 4. Roman → Gujarati (Sentence)
```bash
POST /sentence/en2gu
Content-Type: application/json

{"text": "namaste duniya"}
```

Example:
```bash
curl -X POST http://localhost:8000/sentence/en2gu \
  -H "Content-Type: application/json" \
  -d '{"text": "namaste duniya"}'
```

Response:
```json
{
  "success": true,
  "error": "",
  "at": "2025-11-08 12:00:00 UTC",
  "input": "namaste duniya",
  "result": "નમસ્તે દુનિયા"
}
```

### 5. Gujarati → Roman (Sentence)
```bash
POST /sentence/gu2en
Content-Type: application/json

{"text": "નમસ્તે દુનિયા"}
```

Example:
```bash
curl -X POST http://localhost:8000/sentence/gu2en \
  -H "Content-Type: application/json" \
  -d '{"text": "નમસ્તે દુનિયા"}'
```

Response:
```json
{
  "success": true,
  "error": "",
  "at": "2025-11-08 12:00:00 UTC",
  "input": "નમસ્તે દુનિયા",
  "result": "namaste duniya"
}
```

## Server Options

```bash
python server.py --help
```

Options:
- `--host`: Host to bind to (default: `0.0.0.0`)
- `--port`: Port to bind to (default: `8000`)
- `--debug`: Run in debug mode
- `--preload`: Preload engines at startup
  - `en2gu`: Preload Roman→Gujarati engine
  - `gu2en`: Preload Gujarati→Roman engine
  - `both`: Preload both engines

Example:
```bash
python server.py --port 5000 --preload both
```

## Python Library Usage

You can also use the transliteration engine directly in your Python code:

```python
from xlit_engine import GujaratiXlitEngine

# Roman to Gujarati
engine_en2gu = GujaratiXlitEngine(direction="en2gu", beam_width=4, rescore=True)
results = engine_en2gu.translit_word("namaste", topk=5)
print(results)  # ['નમસ્તે', 'નમસ્ટે', 'નમાસ્તે', 'નમસ્તેં', 'નમસતે']

# Gujarati to Roman
engine_gu2en = GujaratiXlitEngine(direction="gu2en", beam_width=4, rescore=True)
results = engine_gu2en.translit_word("નમસ્તે", topk=5)
print(results)  # ['namaste', 'namastey', 'namasthe', 'namastay', 'namste']

# Sentence transliteration
sentence = engine_en2gu.translit_sentence("namaste duniya")
print(sentence)  # 'નમસ્તે દુનિયા'
```

## Project Structure

```
gujarati_xlit/
├── server.py                 # Flask REST API server
├── requirements.txt          # Python dependencies
├── Dockerfile               # Docker configuration
├── .gitignore              # Git ignore rules
├── README.md               # This file
└── xlit_engine/            # Core transliteration engine
    ├── __init__.py
    ├── gujarati_engine.py  # Main Gujarati engine
    └── transliterator.py   # Fairseq wrapper
```

## Requirements

- Python 3.8+
- PyTorch
- Fairseq
- Flask
- Other dependencies in `requirements.txt`

## Model Details

- **Architecture**: Transformer-based sequence-to-sequence model
- **Framework**: Fairseq (Facebook AI Research)
- **Model Size**: ~150MB (downloaded automatically on first use)
- **Models**: 
  - Roman→Gujarati: `indicxlit-en-indic-v1.0`
  - Gujarati→Roman: `indicxlit-indic-en-v1.0`
- **Source**: [AI4Bharat IndicXlit](https://github.com/AI4Bharat/IndicXlit)

## Performance

- **First request**: Slower (model loading + inference)
- **Subsequent requests**: Fast (~50-200ms per word)
- **Memory**: ~500MB-1GB RAM (model in memory)
- **Preloading**: Use `--preload both` to load models at startup

## Docker Compose (Optional)

Create a `docker-compose.yml`:

```yaml
version: '3.8'

services:
  gujarati-xlit:
    build: .
    ports:
      - "8000:8000"
    environment:
      - PYTHONUNBUFFERED=1
    restart: unless-stopped
    volumes:
      - model-cache:/root/.gujarati_xlit_models

volumes:
  model-cache:
```

Run with:
```bash
docker-compose up -d
```

## Production Deployment

### Using Gunicorn (Recommended)

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 server:app
```

### Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Troubleshooting

### Models not downloading
- Check internet connection
- Ensure sufficient disk space (~200MB)
- Check GitHub access (models hosted on GitHub releases)

### Out of memory
- Reduce beam_width (default: 4, try 2)
- Disable rescoring: `rescore=False`
- Use CPU-only mode if GPU memory is limited

### Slow inference
- Preload engines at startup: `--preload both`
- Use GPU if available (automatic)
- Consider using gunicorn with multiple workers

## License

This project is based on [IndicXlit](https://github.com/AI4Bharat/IndicXlit) by AI4Bharat.

Original work: Copyright (c) AI4Bharat  
License: MIT

## Credits

- **Original Project**: [IndicXlit](https://github.com/AI4Bharat/IndicXlit) by AI4Bharat
- **Research**: [AI4Bharat Transliteration](https://ai4bharat.org/transliteration)
- **Demo**: [xlit.ai4bharat.org](https://xlit.ai4bharat.org)

## Contributing

This is a minimal standalone version. For the full multi-language system, please refer to the [main IndicXlit repository](https://github.com/AI4Bharat/IndicXlit).

## Support

For issues specific to this Gujarati-only version, please check:
1. Server logs for error messages
2. Model download completion
3. Python/PyTorch compatibility

For general transliteration issues, refer to the [IndicXlit repository](https://github.com/AI4Bharat/IndicXlit/issues).
