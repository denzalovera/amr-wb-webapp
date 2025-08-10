#!/bin/bash

# AMR-WB Converter Web Application Startup Script

echo "🎵 Starting AMR-WB Converter Web Application..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Start the web application
echo "🚀 Starting web server on http://localhost:8080"
echo "Press Ctrl+C to stop the server"
python3 app.py