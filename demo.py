#!/usr/bin/env python3
"""
Demo script for the Multi-Agent Query Router
"""

import os
import sys
from main import MultiAgentApp

def run_demo():
    """Run a demonstration of the multi-agent system"""
    
    print("🤖 Multi-Agent Query Router - Demo")
    print("=" * 50)
    
    # Check if API key is set
    if not os.getenv('GOOGLE_API_KEY'):
        print("❌ Error: GOOGLE_API_KEY environment variable not set")
        print("Please set your Google Gemini API key:")
        print("export GOOGLE_API_KEY='your_api_key_here'")
        return
    
    # Initialize the application
    try:
        app = MultiAgentApp()
        print("✅ Application initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize application: {e}")
        return
    
    # Demo queries
    demo_queries = [
        {
            'query': "What is the capital of France?",
            'files': None,
            'description': "Web Search Query"
        },
        {
            'query': "Summarize the key findings in this document",
            'files': ['test_files/sample_text.txt'],
            'description': "File Analysis Query"
        },
        {
            'query': "What is quantum computing and how does it relate to current technology?",
            'files': ['test_files/sample_text.txt'],
            'description': "Combined Query (Web + File)"
        }
    ]
    
    for i, demo in enumerate(demo_queries, 1):
        print(f"\n📋 Demo {i}: {demo['description']}")
        print("-" * 40)
        print(f"Query: {demo['query']}")
        if demo['files']:
            print(f"Files: {demo['files']}")
        
        try:
            # Process the query
            result = app.process_query(demo['query'], demo['files'])
            
            # Display results
            app.display_results(result)
            
        except Exception as e:
            print(f"❌ Error processing query: {e}")
        
        if i < len(demo_queries):
            input("\nPress Enter to continue to next demo...")
    
    print("\n🎉 Demo completed!")
    print("\nTo run the full interactive mode:")
    print("python main.py --interactive")

if __name__ == "__main__":
    run_demo()

