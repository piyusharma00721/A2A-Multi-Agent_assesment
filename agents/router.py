"""
Router Node for query classification and agent selection
"""

import re
from typing import Dict, Any, Tuple

from config import Config

class QueryRouter:
    """Router component that classifies queries and selects appropriate agents"""
    
    def __init__(self):
        """Initialize the router with Gemini model (lazy import/fallback)"""
        if not Config.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY is required. Please set it in your .env file.")
        
        # Lazy import the Gemini chat model. If unavailable, fall back to rule-based router.
        try:
            # Try different import paths for ChatGoogleGenerativeAI
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI  # type: ignore
            except ImportError:
                try:
                    from langchain_community.chat_models import ChatGoogleGenerativeAI  # type: ignore
                except ImportError:
                    from langchain.chat_models import ChatGoogleGenerativeAI  # type: ignore
            
            from langchain.schema import HumanMessage  # type: ignore

            self.HumanMessage = HumanMessage
            self.llm = ChatGoogleGenerativeAI(
                model=Config.GEMINI_MODEL,
                google_api_key=Config.GOOGLE_API_KEY,
                temperature=0.1
            )
            self.use_llm = True
        except Exception as e:
            # Import failed — do not raise here so module import succeeds.
            print(f"Warning: Gemini LLM unavailable ({e}). Falling back to rule-based router.")
            self.llm = None
            self.HumanMessage = None
            self.use_llm = False
    
    def classify_query(self, query: str, has_files: bool = False) -> Tuple[str, str]:
        """
        Classify a query and determine which agent(s) should handle it
        
        Args:
            query: The user's query string
            has_files: Whether files are attached to the query
            
        Returns:
            Tuple of (agent_choice, reasoning)
        """
        # If LLM is not available, use fallback classification
        if not self.use_llm or self.llm is None:
            return self._fallback_classification(query, has_files), "Using rule-based classification (LLM unavailable)"
        
        try:
            prompt = Config.get_router_prompt().format(
                query=query,
                has_files=has_files
            )
            
            response = self.llm.invoke([self.HumanMessage(content=prompt)])
            response_text = response.content.strip()
            
            # Extract agent choice and reasoning
            lines = response_text.split('\n')
            agent_choice = lines[0].strip().upper()
            
            # Validate agent choice
            valid_choices = ['WEB_SEARCH', 'FILE_ANALYSIS', 'BOTH']
            if agent_choice not in valid_choices:
                # Fallback logic based on query content
                agent_choice = self._fallback_classification(query, has_files)
            
            reasoning = '\n'.join(lines[1:]).strip() if len(lines) > 1 else "No reasoning provided"
            
            return agent_choice, reasoning
            
        except Exception as e:
            print(f"Error in query classification: {e}")
            # Fallback to rule-based classification
            return self._fallback_classification(query, has_files), f"Fallback due to error: {str(e)}"
    
    def _fallback_classification(self, query: str, has_files: bool) -> str:
        """
        Fallback rule-based classification when LLM fails
        
        Args:
            query: The user's query string
            has_files: Whether files are attached
            
        Returns:
            Agent choice string
        """
        query_lower = query.lower()
        
        # If files are present, prioritize file analysis
        if has_files:
            # Check if query also needs web search
            web_indicators = ['current', 'latest', 'recent', 'today', 'now', 'weather', 'news']
            if any(indicator in query_lower for indicator in web_indicators):
                return 'BOTH'
            return 'FILE_ANALYSIS'
        
        # Web search indicators
        web_indicators = [
            'what is', 'who is', 'when did', 'where is', 'how to',
            'current', 'latest', 'recent', 'today', 'now',
            'weather', 'news', 'stock', 'price', 'capital of',
            'won', 'championship', 'election', 'covid', 'pandemic'
        ]
        
        if any(indicator in query_lower for indicator in web_indicators):
            return 'WEB_SEARCH'
        
        # Default to web search for general queries
        return 'WEB_SEARCH'
    
    def get_agent_workflow(self, agent_choice: str) -> Dict[str, Any]:
        """
        Get the workflow configuration for the selected agent(s)
        
        Args:
            agent_choice: The selected agent(s)
            
        Returns:
            Workflow configuration dictionary
        """
        workflows = {
            'WEB_SEARCH': {
                'agents': ['web_search'],
                'parallel': False,
                'description': 'Web search only'
            },
            'FILE_ANALYSIS': {
                'agents': ['file_analysis'],
                'parallel': False,
                'description': 'File analysis only'
            },
            'BOTH': {
                'agents': ['web_search', 'file_analysis'],
                'parallel': True,
                'description': 'Both web search and file analysis'
            }
        }
        
        return workflows.get(agent_choice, workflows['WEB_SEARCH'])

