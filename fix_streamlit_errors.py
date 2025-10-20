#!/usr/bin/env python3
"""
Fix script for Streamlit errors
"""

import os
import sys
import subprocess

def create_env_file():
    """Create a proper .env file"""
    print("🔧 Creating .env file...")
    
    env_content = """# Google Gemini API Key (Required)
GOOGLE_API_KEY=your_gemini_api_key_here

# Optional: Custom configurations
MAX_SEARCH_RESULTS=5
CHUNK_SIZE=1500
CHUNK_OVERLAP=200
"""
    
    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        print("✅ .env file created successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def test_imports():
    """Test all imports"""
    print("\n🧪 Testing imports...")
    
    try:
        # Test config import
        from config import Config
        print("✅ Config import successful")
        
        # Test agent imports
        from agents.router import QueryRouter
        print("✅ QueryRouter import successful")
        
        from agents.web_search_agent import WebSearchAgent
        print("✅ WebSearchAgent import successful")
        
        from agents.file_analysis_agent import FileAnalysisAgent
        print("✅ FileAnalysisAgent import successful")
        
        from agents.synthesizer import ResponseSynthesizer
        print("✅ ResponseSynthesizer import successful")
        
        # Test orchestrator import
        from orchestrator import MultiAgentOrchestrator
        print("✅ MultiAgentOrchestrator import successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

def test_orchestrator_creation():
    """Test creating the orchestrator"""
    print("\n🤖 Testing orchestrator creation...")
    
    try:
        from orchestrator import MultiAgentOrchestrator
        orchestrator = MultiAgentOrchestrator()
        print("✅ Orchestrator creation successful")
        return True
    except Exception as e:
        print(f"❌ Orchestrator creation failed: {e}")
        return False

def install_missing_packages():
    """Install any missing packages"""
    print("\n📦 Installing missing packages...")
    
    packages = [
        "langchain-google-genai==0.0.6",
        "sentence-transformers==2.2.2",
        "duckduckgo-search==3.8.6",
        "streamlit==1.28.1",
        "plotly==5.17.0"
    ]
    
    for package in packages:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package], 
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"✅ {package} installed")
        except subprocess.CalledProcessError:
            print(f"⚠️  {package} installation failed (may already be installed)")

def main():
    """Main fix function"""
    print("🔧 Fixing Streamlit Errors")
    print("=" * 40)
    
    # Step 1: Create .env file
    if not create_env_file():
        print("❌ Failed to create .env file")
        return False
    
    # Step 2: Install missing packages
    install_missing_packages()
    
    # Step 3: Test imports
    if not test_imports():
        print("❌ Import tests failed")
        return False
    
    # Step 4: Test orchestrator creation
    if not test_orchestrator_creation():
        print("❌ Orchestrator creation failed")
        return False
    
    print("\n🎉 All fixes applied successfully!")
    print("\n📝 Next steps:")
    print("1. Edit the .env file and add your GOOGLE_API_KEY")
    print("2. Run: streamlit run streamlit_app.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
