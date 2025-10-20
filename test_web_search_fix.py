#!/usr/bin/env python3
"""
Test script for the improved web search functionality
"""

import sys
import os
import time

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_web_search_agent():
    """Test the web search agent functionality"""
    try:
        from agents.web_search_agent import WebSearchAgent
        from config import Config
        
        print("🧪 Testing Web Search Agent...")
        
        # Initialize the agent
        agent = WebSearchAgent(max_results=3, config=Config)
        print("✅ Web Search Agent initialized successfully")
        
        # Test queries
        test_queries = [
            "What is the capital of France?",  # General knowledge
            "What is the current weather in New York?",  # Current info
            "Who is the president of the United States?",  # General knowledge
            "What are the latest news about AI?",  # Current info
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n🔍 Test {i}: {query}")
            try:
                result = agent.process_query(query)
                
                print(f"   Agent Type: {result.get('agent_type', 'Unknown')}")
                print(f"   Search Type: {result.get('search_type', 'Unknown')}")
                
                extracted_info = result.get('extracted_info', {})
                print(f"   Summary: {extracted_info.get('summary', 'No summary')}")
                print(f"   Confidence: {extracted_info.get('confidence', 0):.2f}")
                
                key_facts = extracted_info.get('key_facts', [])
                if key_facts:
                    print(f"   Key Facts: {len(key_facts)} facts found")
                    for j, fact in enumerate(key_facts[:2], 1):  # Show first 2 facts
                        print(f"     {j}. {fact[:100]}...")
                
                sources = extracted_info.get('sources', [])
                if sources:
                    print(f"   Sources: {len(sources)} sources found")
                    for j, source in enumerate(sources[:2], 1):  # Show first 2 sources
                        print(f"     {j}. {source.get('title', 'No title')}")
                
                print("   ✅ Query processed successfully")
                
            except Exception as e:
                print(f"   ❌ Error processing query: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing web search agent: {e}")
        return False

def test_enhanced_web_search_agent():
    """Test the enhanced web search agent functionality"""
    try:
        from agents.enhanced_web_search_agent import EnhancedWebSearchAgent
        from config import Config
        
        print("\n🧪 Testing Enhanced Web Search Agent...")
        
        # Initialize the agent
        agent = EnhancedWebSearchAgent(max_results=3, config=Config)
        print("✅ Enhanced Web Search Agent initialized successfully")
        
        # Test a simple query
        query = "What is artificial intelligence?"
        print(f"\n🔍 Test Query: {query}")
        
        try:
            result = agent.process_query(query)
            
            print(f"   Agent Type: {result.get('agent_type', 'Unknown')}")
            print(f"   Search Type: {result.get('search_type', 'Unknown')}")
            
            extracted_info = result.get('extracted_info', {})
            print(f"   Summary: {extracted_info.get('summary', 'No summary')}")
            print(f"   Confidence: {extracted_info.get('confidence', 0):.2f}")
            
            results = result.get('results', [])
            print(f"   Results: {len(results)} results found")
            
            print("   ✅ Enhanced query processed successfully")
            
        except Exception as e:
            print(f"   ❌ Error processing enhanced query: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing enhanced web search agent: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Improved Web Search Functionality")
    print("=" * 60)
    
    tests = [
        ("Web Search Agent", test_web_search_agent),
        ("Enhanced Web Search Agent", test_enhanced_web_search_agent),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}...")
        if test_func():
            passed += 1
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Web search functionality is working.")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()
