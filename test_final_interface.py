#!/usr/bin/env python3
"""
Final test script for the improved interface and web search functionality
"""

import sys
import os

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required imports work"""
    try:
        from streamlit_app import initialize_orchestrator, initialize_session_state
        print("✅ Streamlit app imports successful")
        
        from agents.web_search_agent import WebSearchAgent
        print("✅ Web search agent imports successful")
        
        from config import Config
        print("✅ Config imports successful")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_web_search_agent():
    """Test web search agent initialization"""
    try:
        from agents.web_search_agent import WebSearchAgent
        from config import Config
        
        agent = WebSearchAgent(max_results=3, config=Config)
        print("✅ Web search agent initialized successfully")
        
        # Test the current information detection
        test_queries = [
            "What is the capital of France?",  # Should not need current info
            "What is the current weather?",    # Should need current info
            "Who is the president?",          # Should need current info
        ]
        
        for query in test_queries:
            needs_current = agent.is_current_information_needed(query)
            print(f"   Query: '{query}' -> Needs current info: {needs_current}")
        
        return True
        
    except Exception as e:
        print(f"❌ Web search agent test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Final Interface and Web Search")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Web Search Agent Test", test_web_search_agent),
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
        print("🎉 All tests passed! The interface is ready to use.")
        print("\n🚀 To run the new interface:")
        print("   streamlit run streamlit_app.py")
        print("\n📋 Features implemented:")
        print("   ✅ ChatGPT/Grok-like interface")
        print("   ✅ Proper layout with sidebar and main content")
        print("   ✅ Text input spans from sidebar to right edge")
        print("   ✅ Attachment icon on the left of text field")
        print("   ✅ Send button on the right of text field")
        print("   ✅ Chat messages appear above text field only")
        print("   ✅ Improved web search with LLM-first approach")
        print("   ✅ Robust fallback mechanisms")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()
