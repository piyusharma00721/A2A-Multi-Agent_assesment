"""
Configuration settings for the Multi-Agent Query Router
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
try:
    load_dotenv()
except Exception as e:
    print(f"Warning: Could not load .env file: {e}")
    print("Please create a .env file with your GOOGLE_API_KEY")

class Config:
    """Configuration class for the application"""
    
    # API Keys
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', '')
    
    # Model Settings
    GEMINI_MODEL = "gemini-2.0-flash"
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Search Settings
    MAX_SEARCH_RESULTS = int(os.getenv('MAX_SEARCH_RESULTS', '5'))
    SEARCH_TIMEOUT = 10
    
    # File Processing Settings
    CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', '1500'))
    CHUNK_OVERLAP = int(os.getenv('CHUNK_OVERLAP', '200'))
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    # Supported file types
    SUPPORTED_EXTENSIONS = {
        '.pdf': 'pdf',
        '.txt': 'text',
        '.csv': 'csv',
        '.xlsx': 'excel',
        '.xls': 'excel',
        '.png': 'image',
        '.jpg': 'image',
        '.jpeg': 'image',
        '.gif': 'image',
        '.bmp': 'image'
    }
    
    # Paths
    DATA_DIR = 'data'
    OUTPUTS_DIR = 'outputs'
    LOGS_DIR = 'logs'
    TEST_FILES_DIR = 'test_files'
    
    # Logging
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    @classmethod
    def validate_config(cls) -> Dict[str, Any]:
        """Validate configuration and return status"""
        issues = []
        
        if not cls.GOOGLE_API_KEY:
            issues.append("GOOGLE_API_KEY is not set")
        
        if cls.CHUNK_SIZE <= 0:
            issues.append("CHUNK_SIZE must be positive")
            
        if cls.CHUNK_OVERLAP < 0:
            issues.append("CHUNK_OVERLAP must be non-negative")
            
        if cls.CHUNK_OVERLAP >= cls.CHUNK_SIZE:
            issues.append("CHUNK_OVERLAP must be less than CHUNK_SIZE")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues
        }
    
    @classmethod
    def get_router_prompt(cls) -> str:
        """Get the router classification prompt"""
        return """You are an intelligent query router for a multi-agent system. 
Your task is to classify incoming queries and determine which agent(s) should handle them.

Available agents:
1. WEB_SEARCH: For queries requiring current information from the internet (news, weather, facts, etc.)
2. FILE_ANALYSIS: For queries about uploaded files (documents, images, spreadsheets, etc.)
3. BOTH: For queries that need both web search and file analysis

Query: "{query}"
Has files attached: {has_files}

Respond with ONLY one of: WEB_SEARCH, FILE_ANALYSIS, or BOTH
Followed by a brief explanation of your reasoning."""

    @classmethod
    def get_synthesis_prompt(cls) -> str:
        """Get the synthesis prompt template"""
        return """You are a response synthesizer. Your task is to combine information from different sources into a coherent, helpful answer.

Question: {query}

Context from agents:
{context}

Instructions:
1. Use only the provided context to answer the question
2. If information is from web search, cite the source URL
3. If information is from file analysis, mention "from the uploaded file"
4. If the context doesn't contain enough information, say so clearly
5. Provide a clear, well-structured answer

Answer:"""

