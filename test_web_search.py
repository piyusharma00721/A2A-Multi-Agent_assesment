#!/usr/bin/env python3
"""
Test script for web search functionality
"""

import sys
import os

def test_duckduckgo():
    """Test DuckDuckGo search functionality"""
    print("🔍 Testing DuckDuckGo Search")
    print("=" * 30)
    
    try:
        from duckduckgo_search import DDGS
        print("✅ DuckDuckGo import successful")
        
        # Test search
        print("Testing search functionality...")
        with DDGS() as ddgs:
            results = list(ddgs.text("test query", max_results=1))
            if results:
                print("✅ Search functionality working")
                print(f"Sample result: {results[0].get('title', 'No title')}")
            else:
                print("⚠️  Search returned no results")
        
        return True
        
    except Exception as e:
        print(f"❌ DuckDuckGo test failed: {e}")
        return False

def test_web_search_agent():
    """Test the web search agent"""
    print("\n🤖 Testing Web Search Agent")
    print("=" * 30)
    
    try:
        from agents.web_search_agent import WebSearchAgent
        print("✅ WebSearchAgent import successful")
        
        # Test agent
        agent = WebSearchAgent()
        print("✅ WebSearchAgent initialization successful")
        
        # Test search
        print("Testing agent search...")
        result = agent.search("capital of France", max_results=2)
        
        if result and len(result) > 0:
            print("✅ Agent search working")
            print(f"Found {len(result)} results")
            if result[0].get('title'):
                print(f"First result: {result[0]['title']}")
        else:
            print("⚠️  Agent search returned no results")
        
        return True
        
    except Exception as e:
        print(f"❌ WebSearchAgent test failed: {e}")
        return False

def test_gemini_imports():
    """Test Gemini imports"""
    print("\n🧠 Testing Gemini Imports")
    print("=" * 30)
    
    try:
        # Test different import paths
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            print("✅ langchain_google_genai import successful")
            return True
        except ImportError:
            try:
                from langchain_community.chat_models import ChatGoogleGenerativeAI
                print("✅ langchain_community.chat_models import successful")
                return True
            except ImportError:
                try:
                    from langchain.chat_models import ChatGoogleGenerativeAI
                    print("✅ langchain.chat_models import successful")
                    return True
                except ImportError:
                    print("❌ All Gemini import paths failed")
                    return False
    except Exception as e:
        print(f"❌ Gemini import test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Testing Multi-Agent Query Router Components")
    print("=" * 50)
    
    tests = [
        ("DuckDuckGo Search", test_duckduckgo),
        ("Web Search Agent", test_web_search_agent),
        ("Gemini Imports", test_gemini_imports)
    ]
    
    passed = 0
    for test_name, test_func in tests:
        print(f"\n🔬 Running {test_name} test...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} test failed")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! The system should work correctly.")
    else:
        print("⚠️  Some tests failed. Check the error messages above.")
        print("\nTo fix issues:")
        print("1. Run: python fix_dependencies.py")
        print("2. Check your GOOGLE_API_KEY environment variable")
        print("3. Ensure all required packages are installed")
    
    return passed == len(tests)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
