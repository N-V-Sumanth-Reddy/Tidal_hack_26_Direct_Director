#!/bin/bash

echo "=========================================="
echo "Ad Video Generation Pipeline Setup"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version
if [ $? -ne 0 ]; then
    echo "Error: Python 3 is not installed"
    exit 1
fi
echo "✓ Python 3 is installed"
echo ""

# Install Python dependencies
echo "Installing Python dependencies..."
python3 -m pip install -q -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Error: Failed to install Python dependencies"
    exit 1
fi
echo "✓ Python dependencies installed"
echo ""

# Check for FFmpeg
echo "Checking for FFmpeg..."
if command -v ffmpeg &> /dev/null; then
    echo "✓ FFmpeg is installed"
    ffmpeg -version | head -1
else
    echo "⚠ FFmpeg is not installed"
    echo ""
    echo "FFmpeg is required for video assembly (Task 9)."
    echo "Please install FFmpeg:"
    echo ""
    echo "  macOS:   brew install ffmpeg"
    echo "  Ubuntu:  sudo apt-get install ffmpeg"
    echo "  Windows: Download from https://ffmpeg.org/download.html"
    echo ""
fi
echo ""

# Create output directories
echo "Creating output directories..."
mkdir -p output
mkdir -p output/scenes
mkdir -p output/storyboard
mkdir -p temp
echo "✓ Output directories created"
echo ""

# Check for .env file
echo "Checking environment configuration..."
if [ -f ".env" ]; then
    echo "✓ .env file exists"
else
    echo "⚠ .env file not found"
    echo ""
    echo "Creating .env from template..."
    cp .env.example .env
    echo "✓ Created .env file"
    echo ""
    echo "IMPORTANT: Please edit .env and add your API keys:"
    echo "  - GEMINI_API_KEY (required)"
    echo "  - TAVILY_API_KEY (required for web search)"
    echo ""
fi

echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env and add your API keys"
echo "2. Run: python3 ad_video_pipeline.py"
echo ""
