#!/usr/bin/env python3
"""
Create .env file for the Multi-Agent Query Router
"""

import os

def create_env_file():
    """Create a .env file with default values"""
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
        print("\n📝 Please edit the .env file and add your actual GOOGLE_API_KEY")
        print("   Replace 'your_gemini_api_key_here' with your real API key")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def main():
    """Main function"""
    print("🔧 Creating .env file for Multi-Agent Query Router")
    print("=" * 50)
    
    if os.path.exists('.env'):
        print("⚠️  .env file already exists")
        response = input("Do you want to overwrite it? (y/n): ")
        if response.lower() != 'y':
            print("Keeping existing .env file")
            return True
    
    if create_env_file():
        print("\n🎯 Next steps:")
        print("1. Edit the .env file and add your GOOGLE_API_KEY")
        print("2. Run: streamlit run streamlit_app.py")
        return True
    else:
        print("\n❌ Failed to create .env file")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
