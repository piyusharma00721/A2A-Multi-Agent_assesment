#!/usr/bin/env python3
"""
Fix script for Multi-Agent Query Router dependencies
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a package using pip"""
    try:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
        print(f"✅ Successfully installed {package}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package}: {e}")
        return False

def main():
    """Main fix function"""
    print("🔧 Fixing Multi-Agent Query Router Dependencies")
    print("=" * 50)
    
    # List of packages to install/update
    packages = [
        "langchain-google-genai==0.0.6",
        "sentence-transformers==2.2.2",
        "duckduckgo-search==3.8.6",
        "torch==2.0.1",
        "transformers==4.35.0",
        "streamlit==1.28.1",
        "plotly==5.17.0"
    ]
    
    print("Installing/updating required packages...")
    
    failed_packages = []
    for package in packages:
        if not install_package(package):
            failed_packages.append(package)
    
    print("\n" + "=" * 50)
    if failed_packages:
        print(f"⚠️  Installation completed with {len(failed_packages)} failures:")
        for package in failed_packages:
            print(f"  - {package}")
        print("\nYou may need to install these packages manually.")
    else:
        print("✅ All packages installed successfully!")
    
    print("\n🔍 Testing imports...")
    
    # Test critical imports
    test_imports = [
        ("langchain_google_genai", "Google Gemini integration"),
        ("sentence_transformers", "Sentence transformers for embeddings"),
        ("duckduckgo_search", "DuckDuckGo search"),
        ("streamlit", "Streamlit UI"),
        ("plotly", "Plotly charts")
    ]
    
    import_success = 0
    for module, description in test_imports:
        try:
            __import__(module)
            print(f"✅ {description}: {module}")
            import_success += 1
        except ImportError as e:
            print(f"❌ {description}: {module} - {e}")
    
    print(f"\n📊 Import Test Results: {import_success}/{len(test_imports)} successful")
    
    if import_success == len(test_imports):
        print("🎉 All dependencies are working correctly!")
        print("\nYou can now run:")
        print("  streamlit run streamlit_app.py")
    else:
        print("⚠️  Some dependencies still need attention.")
        print("Try running the failed imports manually or check for version conflicts.")
    
    return import_success == len(test_imports)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
