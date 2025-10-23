import os
from typing import Dict, Any
from dotenv import load_dotenv
from pydantic import BaseModel, validator

# Load environment variables
try:
    load_dotenv()
except Exception as e:
    print(f"Warning: Could not load .env file: {e}")
    print("Please create a .env file with your GOOGLE_API_KEY")

class Config(BaseModel):
    """Configuration class for the application"""
    
    # API Keys
    google_api_key: str = os.getenv('GOOGLE_API_KEY', '')
    
    # Model Settings
    gemini_model: str = os.getenv('GEMINI_MODEL', "gemini-2.0-flash")
    embedding_model: str = os.getenv('EMBEDDING_MODEL', "sentence-transformers/all-MiniLM-L6-v2")
    
    # Search Settings
    max_search_results: int = int(os.getenv('MAX_SEARCH_RESULTS', '5'))
    search_timeout: int = int(os.getenv('SEARCH_TIMEOUT', '10'))
    
    # File Processing Settings
    chunk_size: int = int(os.getenv('CHUNK_SIZE', '1500'))
    chunk_overlap: int = int(os.getenv('CHUNK_OVERLAP', '200'))
    max_file_size: int = int(os.getenv('MAX_FILE_SIZE_MB', '10')) * 1024 * 1024  # 10MB
    
    # Supported file types
    supported_extensions: Dict[str, str] = {
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
    data_dir: str = 'data'
    outputs_dir: str = 'outputs'
    logs_dir: str = 'logs'
    test_files_dir: str = 'test_files'
    
    # Logging Settings
    log_level: str = os.getenv('LOG_LEVEL', 'INFO')
    log_format: str = os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log_file: str = os.getenv('LOG_FILE', os.path.join('logs', 'app.log'))
    log_max_bytes: int = int(os.getenv('LOG_MAX_BYTES', '10485760'))  # 10MB
    log_backup_count: int = int(os.getenv('LOG_BACKUP_COUNT', '5'))
    
    @validator('google_api_key')
    def validate_api_key(cls, v):
        if not v:
            raise ValueError("GOOGLE_API_KEY is required")
        return v
    
    @validator('chunk_size', 'chunk_overlap', 'max_search_results', 'log_max_bytes', 'log_backup_count')
    def validate_positive(cls, v):
        if v <= 0:
            raise ValueError(f"{v} must be positive")
        return v
    
    @validator('chunk_overlap')
    def validate_overlap(cls, v, values):
        if 'chunk_size' in values and v >= values['chunk_size']:
            raise ValueError("CHUNK_OVERLAP must be less than CHUNK_SIZE")
        return v
    
    @validator('log_level')
    def validate_log_level(cls, v):
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of {valid_levels}")
        return v.upper()
    
    @classmethod
    def instance(cls) -> 'Config':
        """Create and return a validated singleton instance (lazy)"""
        if not hasattr(cls, '_instance'):
            try:
                cls._instance = cls()
                # Create directories
                for path in ['data_dir', 'outputs_dir', 'logs_dir', 'test_files_dir']:
                    os.makedirs(getattr(cls._instance, path), exist_ok=True)
            except ValueError as e:
                print(f"Config validation failed: {e}. Using defaults with warnings.")
                cls._instance = cls(google_api_key='', chunk_size=1, log_level='INFO')
        return cls._instance
    
    @classmethod
    def validate_config(cls) -> Dict[str, Any]:
        """Validate configuration and return status (for Streamlit/UI, non-throwing)"""
        issues = []
        
        # Check API key
        if not os.getenv('GOOGLE_API_KEY'):
            issues.append("GOOGLE_API_KEY is not set")
        
        # Check chunk sizes
        chunk_size = int(os.getenv('CHUNK_SIZE', '1500'))
        chunk_overlap = int(os.getenv('CHUNK_OVERLAP', '200'))
        if chunk_size <= 0:
            issues.append("CHUNK_SIZE must be positive")
        if chunk_overlap < 0:
            issues.append("CHUNK_OVERLAP must be non-negative")
        if chunk_overlap >= chunk_size:
            issues.append("CHUNK_OVERLAP must be less than CHUNK_SIZE")
        
        # Check logging
        log_level = os.getenv('LOG_LEVEL', 'INFO')
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if log_level.upper() not in valid_levels:
            issues.append(f"LOG_LEVEL must be one of {valid_levels}")
        
        # Ensure directories exist
        for path in ['data', 'outputs', 'logs', 'test_files']:
            p = getattr(cls.instance(), path + '_dir') if hasattr(cls.instance(), path + '_dir') else path
            if not os.path.exists(p):
                os.makedirs(p, exist_ok=True)
                print(f"Created directory: {p}")
        
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

# Global instance (lazy init)
config = Config.instance()