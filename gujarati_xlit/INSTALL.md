# Installation Guide - Gujarati Transliteration Server

## Table of Contents
1. [System Requirements](#system-requirements)
2. [Installation Methods](#installation-methods)
3. [Verification](#verification)
4. [Configuration](#configuration)
5. [Troubleshooting](#troubleshooting)

---

## System Requirements

### Minimum
- **OS**: Linux, macOS, or Windows
- **Python**: 3.8 or higher
- **RAM**: 1GB available
- **Disk**: 500MB free space
- **Network**: Internet connection (first run only)

### Recommended
- **OS**: Linux (Ubuntu 20.04+)
- **Python**: 3.9 or 3.10
- **RAM**: 2GB available
- **Disk**: 1GB free space
- **CPU**: 2+ cores
- **GPU**: CUDA-compatible (optional, for faster inference)

---

## Installation Methods

### Method 1: Docker (Recommended for Production)

#### Prerequisites
- Docker installed ([Get Docker](https://docs.docker.com/get-docker/))
- Docker Compose (optional, included in Docker Desktop)

#### Steps

**1. Clone or copy the gujarati_xlit folder**
```bash
cd gujarati_xlit
```

**2. Build the Docker image**
```bash
docker build -t gujarati-xlit:latest .
```

**3. Run the container**
```bash
# Simple run
docker run -p 8000:8000 gujarati-xlit:latest

# With volume for model persistence
docker run -p 8000:8000 \
  -v gujarati-models:/root/.gujarati_xlit_models \
  gujarati-xlit:latest

# Run in background (detached)
docker run -d -p 8000:8000 \
  --name gujarati-xlit-server \
  --restart unless-stopped \
  gujarati-xlit:latest
```

**4. Verify**
```bash
curl http://localhost:8000/health
```

#### Docker Compose (Recommended)

**1. Start**
```bash
docker-compose up -d
```

**2. View logs**
```bash
docker-compose logs -f
```

**3. Stop**
```bash
docker-compose down
```

**4. Update**
```bash
docker-compose down
docker-compose build
docker-compose up -d
```

---

### Method 2: Python Virtual Environment (Recommended for Development)

#### Prerequisites
- Python 3.8+ installed
- pip package manager
- virtualenv (optional but recommended)

#### Steps

**1. Navigate to directory**
```bash
cd gujarati_xlit
```

**2. Create virtual environment**
```bash
# Using venv (built-in)
python3 -m venv venv

# Or using virtualenv
virtualenv venv

# Or using conda
conda create -n gujarati-xlit python=3.9
```

**3. Activate virtual environment**
```bash
# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate

# Conda
conda activate gujarati-xlit
```

**4. Install dependencies**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**5. Run server**
```bash
python server.py
```

#### Quick Setup Script (Linux/macOS)

```bash
chmod +x setup.sh
./setup.sh
source venv/bin/activate
python server.py
```

---

### Method 3: System-wide Installation (Not Recommended)

⚠️ **Warning**: Installs packages globally, may conflict with other projects.

```bash
cd gujarati_xlit
pip install -r requirements.txt
python server.py
```

---

### Method 4: Pip Install (If Published)

```bash
# Future option if package is published to PyPI
pip install gujarati-xlit

# Run server
gujarati-xlit-server

# Or use CLI
gujarati-xlit-cli en2gu namaste
```

---

## Verification

### 1. Check Installation

```bash
# Python packages
pip list | grep -E "flask|fairseq|torch"

# Server file
python server.py --help
```

### 2. Run Health Check

```bash
# Start server first
python server.py

# In another terminal
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "gujarati-xlit",
  "timestamp": "2025-11-08 12:00:00 UTC",
  "engines_loaded": []
}
```

### 3. Test Transliteration

```bash
# Roman to Gujarati
curl "http://localhost:8000/tl/gu/namaste"

# Gujarati to Roman
curl "http://localhost:8000/rtl/gu/નમસ્તે"
```

### 4. Run Test Suite

```bash
pip install requests  # If not installed
python test_api.py
```

---

## Configuration

### Server Options

```bash
python server.py --help
```

Available options:
```
--host HOST        Host to bind to (default: 0.0.0.0)
--port PORT        Port to bind to (default: 8000)
--debug            Run in debug mode
--preload CHOICE   Preload engines: en2gu, gu2en, or both
```

### Examples

**Development mode (with debug)**
```bash
python server.py --debug --port 8000
```

**Production mode (preload both engines)**
```bash
python server.py --preload both
```

**Custom port**
```bash
python server.py --port 5000
```

### Environment Variables

```bash
# Set Python to unbuffered mode (recommended)
export PYTHONUNBUFFERED=1

# Disable GPU (use CPU only)
export CUDA_VISIBLE_DEVICES=""

# Set model cache directory
export GUJARATI_XLIT_MODELS="/custom/path/to/models"
```

### Model Location

Models are automatically downloaded to:
- **Linux/macOS**: `~/.gujarati_xlit_models/`
- **Windows**: `C:\Users\<username>\.gujarati_xlit_models\`
- **Docker**: `/root/.gujarati_xlit_models/`

To use a custom location, modify `gujarati_engine.py`:
```python
models_path = "/your/custom/path"
```

---

## Troubleshooting

### Installation Issues

#### Problem: `pip install` fails with compilation errors

**Solution**: Install build tools
```bash
# Ubuntu/Debian
sudo apt-get install build-essential python3-dev

# CentOS/RHEL
sudo yum install gcc python3-devel

# macOS
xcode-select --install

# Windows
# Install Visual Studio Build Tools
```

#### Problem: PyTorch installation fails

**Solution**: Install PyTorch separately
```bash
# CPU-only version (smaller, faster install)
pip install torch --index-url https://download.pytorch.org/whl/cpu

# Then install other requirements
pip install -r requirements.txt
```

#### Problem: `fairseq` installation fails

**Solution**: Update pip and setuptools
```bash
pip install --upgrade pip setuptools wheel
pip install fairseq
```

### Runtime Issues

#### Problem: Models not downloading

**Symptoms**: Server hangs on first request

**Solutions**:
1. Check internet connection
2. Verify GitHub access:
   ```bash
   curl -I https://github.com/AI4Bharat/IndicXlit/releases
   ```
3. Check disk space:
   ```bash
   df -h ~
   ```
4. Manually download models:
   ```bash
   cd ~/.gujarati_xlit_models
   mkdir -p en2indic/v1.0 indic2en/v1.0
   # Download from: https://github.com/AI4Bharat/IndicXlit/releases/tag/v1.0
   ```

#### Problem: Out of memory

**Symptoms**: Server crashes or becomes unresponsive

**Solutions**:
1. Reduce beam width (edit `server.py`):
   ```python
   beam_width=2  # Instead of 4
   ```
2. Disable rescoring:
   ```python
   rescore=False
   ```
3. Use CPU-only mode:
   ```bash
   export CUDA_VISIBLE_DEVICES=""
   ```
4. Increase system swap space

#### Problem: Slow inference

**Symptoms**: API requests take >5 seconds

**Solutions**:
1. Preload engines:
   ```bash
   python server.py --preload both
   ```
2. Use GPU if available:
   ```bash
   # Check GPU availability
   python -c "import torch; print(torch.cuda.is_available())"
   ```
3. Keep server running (avoid cold starts)
4. Reduce beam width for faster (but less accurate) results

#### Problem: Port already in use

**Symptoms**: `Address already in use` error

**Solutions**:
1. Use different port:
   ```bash
   python server.py --port 5000
   ```
2. Kill existing process:
   ```bash
   # Find process
   lsof -i :8000
   # Kill it
   kill -9 <PID>
   ```

#### Problem: Import errors

**Symptoms**: `ModuleNotFoundError: No module named 'xlit_engine'`

**Solutions**:
1. Ensure you're in the correct directory:
   ```bash
   cd gujarati_xlit
   python server.py
   ```
2. Check virtual environment is activated:
   ```bash
   which python  # Should show venv/bin/python
   ```
3. Reinstall dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Docker Issues

#### Problem: Docker build fails

**Solutions**:
1. Update Docker:
   ```bash
   docker version
   # Update if needed
   ```
2. Clear Docker cache:
   ```bash
   docker system prune -a
   ```
3. Build with no cache:
   ```bash
   docker build --no-cache -t gujarati-xlit .
   ```

#### Problem: Container exits immediately

**Solutions**:
1. Check logs:
   ```bash
   docker logs gujarati-xlit-server
   ```
2. Run interactively:
   ```bash
   docker run -it gujarati-xlit bash
   ```

---

## Post-Installation

### Production Deployment

**1. Use Gunicorn (recommended)**
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 --timeout 120 server:app
```

**2. Set up systemd service (Linux)**
```bash
sudo nano /etc/systemd/system/gujarati-xlit.service
```

Content:
```ini
[Unit]
Description=Gujarati Transliteration Server
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/gujarati_xlit
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/python server.py --preload both
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable gujarati-xlit
sudo systemctl start gujarati-xlit
sudo systemctl status gujarati-xlit
```

**3. Set up nginx reverse proxy**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }
}
```

### Monitoring

**Check server health**
```bash
curl http://localhost:8000/health
```

**Monitor logs**
```bash
# Docker
docker logs gujarati-xlit-server -f

# Systemd
sudo journalctl -u gujarati-xlit -f

# Direct
python server.py 2>&1 | tee server.log
```

---

## Uninstallation

### Docker
```bash
docker-compose down -v  # Remove containers and volumes
docker rmi gujarati-xlit  # Remove image
```

### Python Virtual Environment
```bash
deactivate  # Exit venv
rm -rf venv  # Remove virtual environment
rm -rf ~/.gujarati_xlit_models  # Remove models
```

### System-wide
```bash
pip uninstall -y flask fairseq torch ujson pydload indic-nlp-library
rm -rf ~/.gujarati_xlit_models
```

---

## Next Steps

1. **Read Documentation**: See [README.md](README.md)
2. **Quick Start**: Follow [QUICKSTART.md](QUICKSTART.md)
3. **API Usage**: Test with [test_api.py](test_api.py)
4. **Production**: Configure gunicorn + nginx

---

## Support

### Getting Help
1. Check this guide
2. Review server logs
3. Test with `test_api.py`
4. Check main IndicXlit documentation

### Reporting Issues
- Check logs for error messages
- Verify system requirements
- Include Python/Docker version
- Provide steps to reproduce

---

**Installation complete!** 🎉

Start with: `python server.py --preload both`
