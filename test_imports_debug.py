#!/usr/bin/env python3
"""
Debug script to test imports step by step
"""

import sys
import os

def test_import_step_by_step():
    """Test imports step by step to identify the issue"""
    print("🔍 Testing imports step by step...")
    
    # Test 1: Basic imports
    try:
        import time
        print("✅ time import successful")
    except Exception as e:
        print(f"❌ time import failed: {e}")
        return False
    
    # Test 2: Typing imports
    try:
        from typing import Dict, Any, List, Optional, TypedDict
        print("✅ typing imports successful")
    except Exception as e:
        print(f"❌ typing imports failed: {e}")
        return False
    
    # Test 3: LangGraph imports
    try:
        from langgraph.graph import Graph, StateGraph, END
        print("✅ langgraph imports successful")
    except Exception as e:
        print(f"❌ langgraph imports failed: {e}")
        return False
    
    # Test 4: LangChain imports
    try:
        from langchain.schema import BaseMessage, HumanMessage, AIMessage
        print("✅ langchain imports successful")
    except Exception as e:
        print(f"❌ langchain imports failed: {e}")
        return False
    
    # Test 5: Config import
    try:
        from config import Config
        print("✅ config import successful")
    except Exception as e:
        print(f"❌ config import failed: {e}")
        return False
    
    # Test 6: Agent imports
    try:
        from agents.router import QueryRouter
        print("✅ QueryRouter import successful")
    except Exception as e:
        print(f"❌ QueryRouter import failed: {e}")
        return False
    
    try:
        from agents.web_search_agent import WebSearchAgent
        print("✅ WebSearchAgent import successful")
    except Exception as e:
        print(f"❌ WebSearchAgent import failed: {e}")
        return False
    
    try:
        from agents.file_analysis_agent import FileAnalysisAgent
        print("✅ FileAnalysisAgent import successful")
    except Exception as e:
        print(f"❌ FileAnalysisAgent import failed: {e}")
        return False
    
    try:
        from agents.synthesizer import ResponseSynthesizer
        print("✅ ResponseSynthesizer import successful")
    except Exception as e:
        print(f"❌ ResponseSynthesizer import failed: {e}")
        return False
    
    # Test 7: Orchestrator import
    try:
        from orchestrator import MultiAgentOrchestrator
        print("✅ MultiAgentOrchestrator import successful")
    except Exception as e:
        print(f"❌ MultiAgentOrchestrator import failed: {e}")
        return False
    
    return True

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

def main():
    """Main debug function"""
    print("🐛 Debug Import Issues")
    print("=" * 30)
    
    # Test imports
    if test_import_step_by_step():
        print("\n✅ All imports successful!")
        
        # Test orchestrator creation
        if test_orchestrator_creation():
            print("\n🎉 Everything is working correctly!")
            return True
        else:
            print("\n⚠️  Imports work but orchestrator creation fails")
            return False
    else:
        print("\n❌ Import issues detected")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
