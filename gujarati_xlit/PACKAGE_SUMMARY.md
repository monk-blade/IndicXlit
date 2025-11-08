# Gujarati Transliteration Server - Package Summary

## Overview
A **minimal, portable REST API server** for Gujarati transliteration, supporting bi-directional conversion between Roman and Gujarati scripts.

## Key Features

### ✨ Minimal & Focused
- **Gujarati-only**: No multi-language overhead
- **~150MB models**: Only Gujarati models downloaded
- **Lightweight**: Essential dependencies only

### 🔄 Bi-directional Support
- **Roman → Gujarati**: English script to ગુજરાતી
- **Gujarati → Roman**: ગુજરાતી to English script

### 📦 Portable & Easy
- **Docker ready**: One-command deployment
- **Auto-download**: Models downloaded automatically
- **Self-contained**: All code included

### 🚀 Production Ready
- **REST API**: Standard HTTP/JSON interface
- **Health checks**: Built-in monitoring endpoints
- **Docker Compose**: Easy orchestration

## Package Contents

```
gujarati_xlit/
├── README.md              # Full documentation
├── QUICKSTART.md          # 5-minute setup guide
├── requirements.txt       # Python dependencies
├── setup.sh              # Automated setup script
├── .gitignore            # Git ignore rules
│
├── server.py             # Flask REST API server
├── cli.py                # Command-line interface
├── test_api.py           # API test suite
│
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Docker Compose config
│
└── xlit_engine/          # Core transliteration engine
    ├── __init__.py
    ├── gujarati_engine.py    # Main Gujarati engine
    └── transliterator.py     # Fairseq wrapper
```

## Quick Start Commands

### Docker
```bash
docker build -t gujarati-xlit .
docker run -p 8000:8000 gujarati-xlit
```

### Python
```bash
./setup.sh                      # Setup
source venv/bin/activate        # Activate
python server.py --preload both # Run
```

### Test
```bash
curl http://localhost:8000/tl/gu/namaste
python test_api.py
python cli.py en2gu namaste
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API documentation |
| `/health` | GET | Health check |
| `/tl/gu/<word>` | GET | Roman → Gujarati (word) |
| `/rtl/gu/<word>` | GET | Gujarati → Roman (word) |
| `/sentence/en2gu` | POST | Roman → Gujarati (sentence) |
| `/sentence/gu2en` | POST | Gujarati → Roman (sentence) |

## Architecture

### Components
1. **Flask Server** (`server.py`)
   - REST API endpoints
   - Request/response handling
   - Error management

2. **Gujarati Engine** (`xlit_engine/gujarati_engine.py`)
   - Core transliteration logic
   - Model management
   - Pre/post processing
   - Dictionary rescoring

3. **Transliterator** (`xlit_engine/transliterator.py`)
   - Fairseq model wrapper
   - Batch processing
   - Beam search decoding

### Model Details
- **Framework**: Fairseq (PyTorch)
- **Architecture**: Transformer seq2seq
- **Beam Width**: 4 (configurable)
- **Rescoring**: Dictionary-based (optional)
- **Source**: AI4Bharat IndicXlit v1.0

## Dependencies

### Core
- `flask` - Web framework
- `fairseq` - Transformer models
- `torch` - PyTorch backend
- `indic-nlp-library` - Text normalization

### Utilities
- `ujson` - Fast JSON parsing
- `pydload` - File downloads
- `sacremoses` - Tokenization
- `tqdm` - Progress bars

## Performance

| Metric | Value |
|--------|-------|
| First request | 2-5 seconds (model loading) |
| Subsequent requests | 50-200ms per word |
| Memory usage | 500MB - 1GB |
| Model size | ~150MB |
| Cold start (Docker) | 30-60 seconds |

## Comparison with Full IndicXlit

| Feature | Full IndicXlit | Gujarati-only |
|---------|---------------|---------------|
| Languages | 21+ | 1 (Gujarati) |
| Model size | ~3GB | ~150MB |
| Memory | 2-4GB | 500MB-1GB |
| Dependencies | 15+ packages | 10 packages |
| Lines of code | ~10K+ | ~800 |
| Setup time | 10-15 min | 2-3 min |

**Size reduction**: ~95% smaller models, ~50% less dependencies

## Use Cases

### 1. Input Method Enhancement
- Real-time transliteration suggestions
- Mobile/web keyboard apps
- Chat applications

### 2. Content Conversion
- Batch transliteration of documents
- Website content localization
- Social media text conversion

### 3. Search & Indexing
- Romanized search in Gujarati content
- Cross-script name matching
- Database normalization

### 4. Educational Tools
- Language learning apps
- Script conversion practice
- Pronunciation guides

## Deployment Options

### Development
```bash
python server.py --debug
```

### Docker
```bash
docker-compose up -d
```

### Production (Gunicorn)
```bash
gunicorn -w 4 -b 0.0.0.0:8000 server:app
```

### Cloud (Example: AWS EC2)
```bash
# On EC2 instance
git clone <repo>
cd gujarati_xlit
docker-compose up -d
# Configure security groups for port 8000
```

## Customization

### Change Beam Width
Edit `server.py`:
```python
engine = GujaratiXlitEngine(direction=direction, beam_width=8)  # Default: 4
```

### Disable Rescoring (Faster)
```python
engine = GujaratiXlitEngine(direction=direction, rescore=False)
```

### Change Port
```bash
python server.py --port 5000
```

### Add Authentication
Add to `server.py`:
```python
from functools import wraps

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if token != 'Bearer YOUR_TOKEN':
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/tl/gu/<word>')
@require_auth
def transliterate_en2gu(word):
    ...
```

## Testing

### Unit Tests (Manual)
```python
from xlit_engine import GujaratiXlitEngine

engine = GujaratiXlitEngine("en2gu")
assert "નમસ્તે" in engine.translit_word("namaste", topk=5)
```

### Integration Tests
```bash
python test_api.py
```

### Load Testing (Example)
```bash
# Install Apache Bench
apt-get install apache2-utils

# Test
ab -n 1000 -c 10 http://localhost:8000/tl/gu/namaste
```

## Monitoring

### Health Check
```bash
curl http://localhost:8000/health
```

### Docker Logs
```bash
docker logs gujarati-xlit-server -f
```

### Metrics to Track
- Response time
- Error rate
- Memory usage
- Model load time

## Security Considerations

### Recommendations
1. **Rate limiting**: Add Flask-Limiter
2. **Authentication**: Implement API keys
3. **HTTPS**: Use reverse proxy (nginx)
4. **Input validation**: Already included
5. **CORS**: Configure for your domain

### Production Checklist
- [ ] Disable debug mode
- [ ] Set up HTTPS
- [ ] Implement authentication
- [ ] Configure rate limiting
- [ ] Set up monitoring
- [ ] Regular backups
- [ ] Update dependencies

## Troubleshooting

### Common Issues

**Models not downloading**
- Check internet connection
- Verify GitHub access
- Ensure disk space (~200MB)

**Out of memory**
- Reduce beam_width (2 or 3)
- Disable rescoring
- Use CPU-only mode

**Slow inference**
- Preload engines at startup
- Use GPU if available
- Consider caching results

**Port conflicts**
- Change port: `--port 5000`
- Check: `lsof -i :8000`

## Future Enhancements

### Potential Improvements
- [ ] Result caching (Redis)
- [ ] Rate limiting
- [ ] API authentication
- [ ] Metrics/analytics
- [ ] Batch processing endpoint
- [ ] WebSocket support
- [ ] Model quantization (smaller size)
- [ ] GPU acceleration support

## Credits & License

### Based On
- **IndicXlit**: https://github.com/AI4Bharat/IndicXlit
- **AI4Bharat**: https://ai4bharat.org
- **Research**: https://ai4bharat.org/transliteration

### License
MIT License (same as IndicXlit)

### Authors
- Original: AI4Bharat Team
- Gujarati-only adaptation: Extracted and optimized for single language

## Support

### Documentation
- `README.md` - Full documentation
- `QUICKSTART.md` - Quick setup guide
- This file - Package summary

### Getting Help
1. Check documentation
2. Review server logs
3. Test with `test_api.py`
4. Refer to IndicXlit issues: https://github.com/AI4Bharat/IndicXlit/issues

## Version History

### v1.0.0 (Current)
- Initial release
- Roman ↔ Gujarati transliteration
- REST API server
- Docker support
- CLI interface
- Comprehensive documentation

---

**Total Package Size**: ~2MB (code) + ~150MB (models, auto-downloaded)

**Setup Time**: 2-3 minutes (with good internet)

**Ready for**: Development, Testing, Production
