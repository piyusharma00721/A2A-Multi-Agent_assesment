#!/usr/bin/env python3
"""
Test script to check if all imports work correctly
"""

import sys
import os

def test_import(module_name, description):
    """Test if a module can be imported"""
    try:
        __import__(module_name)
        print(f"✅ {description}: {module_name}")
        return True
    except ImportError as e:
        print(f"❌ {description}: {module_name} - {e}")
        return False

def main():
    """Test all required imports"""
    print("🧪 Testing Multi-Agent Query Router Imports")
    print("=" * 50)
    
    # Test core Python modules
    core_modules = [
        ("os", "Operating System Interface"),
        ("sys", "System-specific Parameters"),
        ("time", "Time-related Functions"),
        ("json", "JSON Data Handling"),
        ("uuid", "UUID Generation"),
        ("datetime", "Date and Time"),
        ("typing", "Type Hints"),
        ("re", "Regular Expressions"),
    ]
    
    print("\n📋 Core Python Modules:")
    core_success = 0
    for module, desc in core_modules:
        if test_import(module, desc):
            core_success += 1
    
    # Test third-party modules
    third_party_modules = [
        ("dotenv", "Environment Variables"),
        ("langchain", "LangChain Core"),
        ("langchain_community", "LangChain Community"),
        ("langgraph", "LangGraph"),
        ("google.generativeai", "Google Generative AI"),
        ("faiss", "FAISS Vector Search"),
        ("pytesseract", "Tesseract OCR"),
        ("fitz", "PyMuPDF"),
        ("pandas", "Pandas Data Analysis"),
        ("PIL", "Pillow Image Processing"),
        ("duckduckgo_search", "DuckDuckGo Search"),
        ("sentence_transformers", "Sentence Transformers"),
    ]
    
    print("\n📦 Third-party Modules:")
    third_party_success = 0
    for module, desc in third_party_modules:
        if test_import(module, desc):
            third_party_success += 1
    
    # Test our custom modules
    custom_modules = [
        ("config", "Configuration Module"),
        ("agents.router", "Query Router"),
        ("agents.web_search_agent", "Web Search Agent"),
        ("agents.file_analysis_agent", "File Analysis Agent"),
        ("agents.synthesizer", "Response Synthesizer"),
        ("orchestrator", "Multi-Agent Orchestrator"),
        ("utils.logger", "Logging System"),
    ]
    
    print("\n🏗️  Custom Modules:")
    custom_success = 0
    for module, desc in custom_modules:
        if test_import(module, desc):
            custom_success += 1
    
    # Summary
    total_modules = len(core_modules) + len(third_party_modules) + len(custom_modules)
    total_success = core_success + third_party_success + custom_success
    
    print("\n" + "=" * 50)
    print(f"📊 Import Test Results:")
    print(f"  Core Modules: {core_success}/{len(core_modules)}")
    print(f"  Third-party: {third_party_success}/{len(third_party_modules)}")
    print(f"  Custom: {custom_success}/{len(custom_modules)}")
    print(f"  Total: {total_success}/{total_modules}")
    
    if total_success == total_modules:
        print("✅ All imports successful! System is ready to run.")
        return True
    else:
        print("⚠️  Some imports failed. System may have limited functionality.")
        print("\nTo fix missing dependencies:")
        print("  python install_dependencies.py")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
