#!/usr/bin/env python3
"""
Streamlit launcher script for Multi-Agent Query Router
"""

import subprocess
import sys
import os
import webbrowser
import time
from threading import Timer

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import streamlit
        import plotly
        print("✅ Streamlit and Plotly are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install required packages:")
        print("pip install streamlit plotly")
        return False

def open_browser():
    """Open browser after a short delay"""
    webbrowser.open('http://localhost:8501')

def main():
    """Main launcher function"""
    print("🚀 Starting Multi-Agent Query Router Streamlit App")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("⚠️  Warning: .env file not found")
        print("Please create a .env file with your GOOGLE_API_KEY")
        print("Example: GOOGLE_API_KEY=your_api_key_here")
        print()
    
    # Check if API key is set
    if not os.getenv('GOOGLE_API_KEY'):
        print("⚠️  Warning: GOOGLE_API_KEY environment variable not set")
        print("The system will work with limited functionality")
        print()
    
    print("🌐 Starting Streamlit server...")
    print("📱 The app will open in your browser automatically")
    print("🔗 Manual access: http://localhost:8501")
    print("⏹️  Press Ctrl+C to stop the server")
    print()
    
    # Open browser after 2 seconds
    Timer(2.0, open_browser).start()
    
    try:
        # Run Streamlit
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', 'streamlit_app.py',
            '--server.port', '8501',
            '--server.address', 'localhost',
            '--browser.gatherUsageStats', 'false'
        ])
    except KeyboardInterrupt:
        print("\n👋 Streamlit server stopped")
    except Exception as e:
        print(f"❌ Error starting Streamlit: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
