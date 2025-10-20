#!/usr/bin/env python3
"""
Setup script for Multi-Agent Query Router POC
"""

import os
import json
import subprocess
import sys

def create_directories():
    """Create necessary directories"""
    dirs = ['data', 'outputs', 'test_files', 'logs']
    for dir_name in dirs:
        os.makedirs(dir_name, exist_ok=True)
        print(f"Created directory: {dir_name}")

def create_initial_files():
    """Create initial configuration and data files"""
    # Initialize empty requests log
    with open('outputs/requests.json', 'w') as f:
        json.dump([], f)
    
    # Create .env template
    env_template = """# Google Gemini API Key
GOOGLE_API_KEY=your_gemini_api_key_here

# Optional: Custom configurations
MAX_SEARCH_RESULTS=5
CHUNK_SIZE=1500
CHUNK_OVERLAP=200
"""
    with open('.env.template', 'w') as f:
        f.write(env_template)
    
    print("Created initial configuration files")

def install_dependencies():
    """Install required dependencies"""
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        return False
    return True

def main():
    print("Setting up Multi-Agent Query Router POC...")
    
    create_directories()
    create_initial_files()
    
    if install_dependencies():
        print("\nSetup completed successfully!")
        print("\nNext steps:")
        print("1. Copy .env.template to .env and add your Google API key")
        print("2. Run: python main.py --help")
    else:
        print("\nSetup failed. Please check the error messages above.")

if __name__ == "__main__":
    main()

