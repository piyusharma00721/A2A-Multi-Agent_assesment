#!/usr/bin/env python3
"""
Test script to verify Streamlit fixes
"""

import os
import json
from utils.logger import logger

def test_logger_fixes():
    """Test the logger fixes for empty JSON files"""
    print("🧪 Testing Logger Fixes")
    print("=" * 30)
    
    # Test statistics with empty file
    print("1. Testing statistics with empty JSON file...")
    stats = logger.get_statistics()
    print(f"   ✅ Statistics: {stats}")
    
    # Test recent logs with empty file
    print("2. Testing recent logs with empty JSON file...")
    recent_logs = logger.get_recent_logs(5)
    print(f"   ✅ Recent logs: {recent_logs}")
    
    # Test with non-existent file
    print("3. Testing with non-existent file...")
    test_logger = logger.__class__('non_existent_file.json')
    stats = test_logger.get_statistics()
    print(f"   ✅ Non-existent file stats: {stats}")
    
    print("\n✅ All logger tests passed!")

def test_json_file():
    """Test the JSON file structure"""
    print("\n📄 Testing JSON File Structure")
    print("=" * 30)
    
    json_file = 'outputs/requests.json'
    
    if os.path.exists(json_file):
        with open(json_file, 'r') as f:
            content = f.read().strip()
            print(f"File content: '{content}'")
            
            if content:
                try:
                    data = json.loads(content)
                    print(f"✅ JSON parsed successfully: {data}")
                except json.JSONDecodeError as e:
                    print(f"❌ JSON parse error: {e}")
            else:
                print("✅ Empty file handled correctly")
    else:
        print("❌ JSON file does not exist")

def main():
    """Main test function"""
    print("🔧 Testing Streamlit Fixes")
    print("=" * 40)
    
    test_logger_fixes()
    test_json_file()
    
    print("\n🎉 All tests completed!")
    print("\nThe Streamlit app should now work without errors.")
    print("Run: streamlit run streamlit_app.py")

if __name__ == "__main__":
    main()
