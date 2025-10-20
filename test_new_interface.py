#!/usr/bin/env python3
"""
Test script for the new ChatGPT/Grok-like interface
"""

import streamlit as st
import sys
import os

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required imports work"""
    try:
        from streamlit_app import initialize_orchestrator, initialize_session_state
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_session_state():
    """Test session state initialization"""
    try:
        # Import the function
        from streamlit_app import initialize_session_state
        
        # Mock streamlit session state
        class MockSessionState:
            def __init__(self):
                self.data = {}
            
            def __getitem__(self, key):
                return self.data.get(key)
            
            def __setitem__(self, key, value):
                self.data[key] = value
            
            def get(self, key, default=None):
                return self.data.get(key, default)
        
        # Mock st.session_state
        st.session_state = MockSessionState()
        
        # Test initialization
        initialize_session_state()
        
        # Check that all required keys are set
        required_keys = ['messages', 'file_paths', 'chat_history', 'current_conversation', 'uploaded_files']
        for key in required_keys:
            if key not in st.session_state.data:
                print(f"❌ Missing session state key: {key}")
                return False
        
        print("✅ Session state initialization successful")
        return True
        
    except Exception as e:
        print(f"❌ Session state error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing new ChatGPT/Grok-like interface...")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Session State Test", test_session_state),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name}...")
        if test_func():
            passed += 1
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The new interface is ready to use.")
        print("\n🚀 To run the new interface:")
        print("   streamlit run streamlit_app.py")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()
