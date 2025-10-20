#!/bin/bash

# Multi-Agent Query Router - Demo Runner
# This script sets up and runs the demo

echo "🤖 Multi-Agent Query Router - Demo Setup"
echo "========================================"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Check for API key
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "⚠️  Warning: GOOGLE_API_KEY environment variable not set"
    echo "Please set your Google Gemini API key:"
    echo "export GOOGLE_API_KEY='your_api_key_here'"
    echo ""
    echo "You can also create a .env file with:"
    echo "GOOGLE_API_KEY=your_api_key_here"
    echo ""
    read -p "Do you want to continue anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data outputs logs test_files

# Initialize empty log file
echo "[]" > outputs/requests.json

echo ""
echo "🚀 Starting demo..."
echo "=================="

# Run the demo
python demo.py

echo ""
echo "✅ Demo completed!"
echo ""
echo "To run the full interactive mode:"
echo "python main.py --interactive"
echo ""
echo "To view system statistics:"
echo "python main.py --stats"
echo ""
echo "To run tests:"
echo "python tests/test_queries.py"

