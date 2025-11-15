#!/bin/bash

# Google PAA Scraper - Web Server Startup Script

set -e

echo "🔥 Google PAA Scraper - Web Interface"
echo "======================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Clean up old virtual environment to ensure fresh install
if [ -d "venv" ]; then
    echo "Removing old virtual environment..."
    rm -rf venv
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Check for .env file
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  No .env file found!"
    echo "Please create a .env file with your Firecrawl API key:"
    echo ""
    echo "    echo 'FIRECRAWL_API_KEY=your_key_here' > .env"
    echo ""
    echo "You can get a free API key from: https://firecrawl.dev"
    echo ""
fi

# Start the Flask app
echo ""
echo "Starting web server..."
echo "Open your browser and go to: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python3 app.py
