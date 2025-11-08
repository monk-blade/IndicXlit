#!/bin/bash
# Quick start script for Gujarati Transliteration Server

set -e

echo "=========================================="
echo "Gujarati Transliteration Server Setup"
echo "=========================================="
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Dependencies installed"

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "To start the server:"
echo "  source venv/bin/activate"
echo "  python server.py"
echo ""
echo "Or with options:"
echo "  python server.py --port 8000 --preload both"
echo ""
echo "Access the API at: http://localhost:8000"
echo "=========================================="
