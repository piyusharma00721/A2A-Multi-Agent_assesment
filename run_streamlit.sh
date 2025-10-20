#!/bin/bash

# Streamlit launcher for Multi-Agent Query Router (Linux/Mac)

echo "🚀 Starting Multi-Agent Query Router Streamlit App"
echo "=================================================="

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

# Install dependencies if needed
echo "📚 Checking dependencies..."
pip install streamlit plotly > /dev/null 2>&1

# Check for API key
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "⚠️  Warning: GOOGLE_API_KEY environment variable not set"
    echo "The system will work with limited functionality"
    echo ""
fi

echo "🌐 Starting Streamlit server..."
echo "📱 The app will open in your browser automatically"
echo "🔗 Manual access: http://localhost:8501"
echo "⏹️  Press Ctrl+C to stop the server"
echo ""

# Run Streamlit
python -m streamlit run streamlit_app.py --server.port 8501 --server.address localhost --browser.gatherUsageStats false
