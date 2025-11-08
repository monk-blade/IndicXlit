# Quick Start Guide - Gujarati Transliteration Server

Get up and running in 5 minutes! 🚀

## Prerequisites

- Python 3.8+ **OR** Docker
- ~500MB disk space (for models)
- Internet connection (for first-time model download)

## Method 1: Docker (Easiest) 🐳

### Step 1: Build and Run
```bash
cd gujarati_xlit

# Build the image
docker build -t gujarati-xlit .

# Run the server
docker run -p 8000:8000 gujarati-xlit
```

### Step 2: Test It
```bash
# In another terminal
curl http://localhost:8000/tl/gu/namaste
```

**Done!** ✓

---

## Method 2: Python Virtual Environment 🐍

### Step 1: Setup
```bash
cd gujarati_xlit

# Run the setup script
chmod +x setup.sh
./setup.sh
```

### Step 2: Start Server
```bash
# Activate virtual environment
source venv/bin/activate

# Start the server
python server.py

# Or with preloading both engines
python server.py --preload both
```

### Step 3: Test It
```bash
# In another terminal
curl http://localhost:8000/tl/gu/namaste
```

**Done!** ✓

---

## Method 3: Direct Install (Advanced) ⚡

### Step 1: Install Dependencies
```bash
cd gujarati_xlit
pip install -r requirements.txt
```

### Step 2: Run Server
```bash
python server.py
```

**Done!** ✓

---

## Test the API

### Option A: Using the Test Script
```bash
# Install requests if not already installed
pip install requests

# Run the test suite
python test_api.py
```

### Option B: Manual Testing

**1. Health Check**
```bash
curl http://localhost:8000/health
```

**2. Roman to Gujarati (Word)**
```bash
curl "http://localhost:8000/tl/gu/namaste?num_suggestions=3"
```

**3. Gujarati to Roman (Word)**
```bash
curl "http://localhost:8000/rtl/gu/નમસ્તે?num_suggestions=3"
```

**4. Roman to Gujarati (Sentence)**
```bash
curl -X POST http://localhost:8000/sentence/en2gu \
  -H "Content-Type: application/json" \
  -d '{"text": "namaste duniya"}'
```

**5. Gujarati to Roman (Sentence)**
```bash
curl -X POST http://localhost:8000/sentence/gu2en \
  -H "Content-Type: application/json" \
  -d '{"text": "નમસ્તે દુનિયા"}'
```

### Option C: Using the CLI
```bash
# Roman to Gujarati
python cli.py en2gu namaste

# Gujarati to Roman
python cli.py gu2en "નમસ્તે"

# Sentence
python cli.py en2gu "namaste duniya"
```

---

## Common Issues & Solutions

### 1. Models Not Downloading
**Problem**: First request fails or hangs  
**Solution**: 
- Check internet connection
- Ensure you have ~200MB free space
- Wait for automatic download (may take 2-3 minutes)

### 2. Import Errors
**Problem**: `ModuleNotFoundError`  
**Solution**:
```bash
pip install -r requirements.txt
```

### 3. Port Already in Use
**Problem**: `Address already in use`  
**Solution**:
```bash
# Use a different port
python server.py --port 5000
```

### 4. Slow First Request
**Problem**: First API call takes long  
**Solution**: This is normal! Models are loading. Use `--preload both` to load at startup:
```bash
python server.py --preload both
```

---

## Docker Compose (Production)

### Step 1: Start
```bash
docker-compose up -d
```

### Step 2: Check Logs
```bash
docker-compose logs -f
```

### Step 3: Stop
```bash
docker-compose down
```

---

## Next Steps

1. **Read Full Documentation**: See [README.md](README.md) for detailed API docs
2. **Integrate**: Use the API in your application
3. **Production**: Set up with gunicorn + nginx (see README.md)

---

## Quick Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/tl/gu/<word>` | GET | Roman → Gujarati (word) |
| `/rtl/gu/<word>` | GET | Gujarati → Roman (word) |
| `/sentence/en2gu` | POST | Roman → Gujarati (sentence) |
| `/sentence/gu2en` | POST | Gujarati → Roman (sentence) |

---

## Need Help?

- Check logs: `docker logs gujarati-xlit-server` (Docker) or terminal output (Python)
- Verify server is running: `curl http://localhost:8000/health`
- Ensure dependencies are installed: `pip list | grep fairseq`

---

**Happy Transliterating!** 🎉
