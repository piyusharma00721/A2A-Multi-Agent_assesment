"""
Synthesizer component for combining agent outputs into coherent responses
"""

import os
import time
from typing import Dict, Any, List, Optional
from config import Config

class ResponseSynthesizer:
    """Component responsible for synthesizing responses from multiple agents"""
    
    def __init__(self):
        """Initialize the synthesizer with Gemini model (lazy import/fallback)"""
        if not Config.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY is required. Please set it in your .env file.")
        
        # Lazy import the Gemini chat model. If unavailable, fall back to simple text synthesis.
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
            from langchain.prompts import PromptTemplate  # type: ignore

            self.HumanMessage = HumanMessage
            self.llm = ChatGoogleGenerativeAI(
                model=Config.GEMINI_MODEL,
                google_api_key=Config.GOOGLE_API_KEY,
                temperature=0.3
            )
            
            self.synthesis_prompt = PromptTemplate(
                input_variables=["query", "context"],
                template=Config.get_synthesis_prompt()
            )
            self.use_llm = True
        except Exception as e:
            # Import failed — do not raise here so module import succeeds.
            print(f"Warning: Gemini LLM unavailable ({e}). Falling back to simple text synthesis.")
            self.llm = None
            self.HumanMessage = None
            self.synthesis_prompt = None
            self.use_llm = False
    
    def format_web_search_context(self, web_results: Dict[str, Any]) -> str:
        """
        Format web search results into context string
        
        Args:
            web_results: Results from web search agent
            
        Returns:
            Formatted context string
        """
        if not web_results or not web_results.get('results'):
            return "No web search results available."
        
        context_parts = ["=== WEB SEARCH RESULTS ==="]
        
        # Add extracted information summary
        extracted_info = web_results.get('extracted_info', {})
        if extracted_info:
            context_parts.append(f"Summary: {extracted_info.get('summary', 'No summary available')}")
            
            key_facts = extracted_info.get('key_facts', [])
            if key_facts:
                context_parts.append("Key Facts:")
                for i, fact in enumerate(key_facts, 1):
                    context_parts.append(f"{i}. {fact}")
        
        # Add individual search results
        results = web_results.get('results', [])
        for result in results[:3]:  # Limit to top 3 results
            if not result.get('error', False):
                context_parts.append(f"\nSource: {result.get('title', 'No title')}")
                context_parts.append(f"URL: {result.get('url', 'No URL')}")
                context_parts.append(f"Content: {result.get('snippet', 'No content')}")
        
        return "\n".join(context_parts)
    
    def format_file_analysis_context(self, file_results: Dict[str, Any]) -> str:
        """
        Format file analysis results into context string
        
        Args:
            file_results: Results from file analysis agent
            
        Returns:
            Formatted context string
        """
        if not file_results:
            return "No file analysis results available."
        
        context_parts = ["=== FILE ANALYSIS RESULTS ==="]
        
        # Add processing summary
        files_processed = file_results.get('files_processed', 0)
        total_chunks = file_results.get('total_chunks', 0)
        context_parts.append(f"Files processed: {files_processed}")
        context_parts.append(f"Text chunks created: {total_chunks}")
        
        # Add search results if available
        search_results = file_results.get('search_results', [])
        if search_results:
            context_parts.append("\nRelevant content from files:")
            for i, result in enumerate(search_results, 1):
                context_parts.append(f"\n{i}. Similarity Score: {result.get('similarity_score', 0):.3f}")
                context_parts.append(f"Source: {result.get('metadata', {}).get('file_path', 'Unknown file')}")
                context_parts.append(f"Content: {result.get('content', 'No content')}")
        else:
            # Add processing results for each file
            processing_results = file_results.get('processing_results', [])
            for result in processing_results:
                if result.get('success', False):
                    metadata = result.get('metadata', {})
                    file_type = metadata.get('file_type', 'unknown')
                    context_parts.append(f"\nFile: {result.get('file_path', 'Unknown')}")
                    context_parts.append(f"Type: {file_type}")
                    
                    # Add specific metadata based on file type
                    if file_type == 'pdf':
                        page_count = metadata.get('page_count', 0)
                        context_parts.append(f"Pages: {page_count}")
                    elif file_type == 'tabular':
                        rows = metadata.get('rows', 0)
                        cols = metadata.get('columns', 0)
                        context_parts.append(f"Data: {rows} rows, {cols} columns")
                    elif file_type == 'image':
                        image_size = metadata.get('image_size', 'Unknown')
                        context_parts.append(f"Image size: {image_size}")
                else:
                    error = result.get('metadata', {}).get('error', 'Unknown error')
                    context_parts.append(f"\nFile: {result.get('file_path', 'Unknown')} - Error: {error}")
        
        return "\n".join(context_parts)
    
    def combine_contexts(self, web_results: Optional[Dict[str, Any]] = None, 
                        file_results: Optional[Dict[str, Any]] = None) -> str:
        """
        Combine contexts from different agents
        
        Args:
            web_results: Results from web search agent
            file_results: Results from file analysis agent
            
        Returns:
            Combined context string
        """
        contexts = []
        
        if web_results:
            web_context = self.format_web_search_context(web_results)
            contexts.append(web_context)
        
        if file_results:
            file_context = self.format_file_analysis_context(file_results)
            contexts.append(file_context)
        
        if not contexts:
            return "No context available from any agent."
        
        return "\n\n".join(contexts)
    
    def synthesize_response(self, query: str, web_results: Optional[Dict[str, Any]] = None,
                          file_results: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Synthesize a coherent response from agent results
        
        Args:
            query: Original user query
            web_results: Results from web search agent
            file_results: Results from file analysis agent
            
        Returns:
            Dictionary with synthesized response and metadata
        """
        try:
            # Combine contexts from all agents
            context = self.combine_contexts(web_results, file_results)
            
            # If LLM is not available, use simple text synthesis
            if not self.use_llm or self.llm is None:
                synthesized_answer = self._simple_text_synthesis(query, context)
                synthesis_method = 'simple_text_fallback'
            else:
                # Generate synthesis prompt
                prompt = self.synthesis_prompt.format(query=query, context=context)
                
                # Get response from LLM
                response = self.llm.invoke([self.HumanMessage(content=prompt)])
                synthesized_answer = response.content.strip()
                synthesis_method = 'gemini_llm'
            
            # Calculate confidence based on available information
            confidence = self._calculate_confidence(web_results, file_results)
            
            # Generate citations
            citations = self._extract_citations(web_results, file_results)
            
            return {
                'query': query,
                'answer': synthesized_answer,
                'context_used': context,
                'confidence': confidence,
                'citations': citations,
                'sources': {
                    'web_search': web_results is not None,
                    'file_analysis': file_results is not None
                },
                'timestamp': time.time(),
                'synthesis_method': synthesis_method
            }
            
        except Exception as e:
            return {
                'query': query,
                'answer': f"Error synthesizing response: {str(e)}",
                'context_used': '',
                'confidence': 0.0,
                'citations': [],
                'sources': {
                    'web_search': web_results is not None,
                    'file_analysis': file_results is not None
                },
                'timestamp': time.time(),
                'synthesis_method': 'error_fallback',
                'error': str(e)
            }
    
    def _calculate_confidence(self, web_results: Optional[Dict[str, Any]] = None,
                            file_results: Optional[Dict[str, Any]] = None) -> float:
        """
        Calculate confidence score based on available information
        
        Args:
            web_results: Results from web search agent
            file_results: Results from file analysis agent
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        confidence = 0.0
        
        # Web search confidence
        if web_results:
            web_confidence = web_results.get('extracted_info', {}).get('confidence', 0.0)
            confidence += web_confidence * 0.6  # Weight web search more for general queries
        
        # File analysis confidence
        if file_results:
            search_results = file_results.get('search_results', [])
            if search_results:
                # Average similarity score of top results
                avg_similarity = sum(r.get('similarity_score', 0) for r in search_results) / len(search_results)
                confidence += avg_similarity * 0.4
        
        return min(1.0, confidence)
    
    def _extract_citations(self, web_results: Optional[Dict[str, Any]] = None,
                         file_results: Optional[Dict[str, Any]] = None) -> List[Dict[str, str]]:
        """
        Extract citations from agent results
        
        Args:
            web_results: Results from web search agent
            file_results: Results from file analysis agent
            
        Returns:
            List of citation dictionaries
        """
        citations = []
        
        # Web search citations
        if web_results and web_results.get('results'):
            for result in web_results['results']:
                if not result.get('error', False) and result.get('url'):
                    citations.append({
                        'type': 'web',
                        'title': result.get('title', 'Web Source'),
                        'url': result.get('url', ''),
                        'snippet': result.get('snippet', '')[:100] + '...' if len(result.get('snippet', '')) > 100 else result.get('snippet', '')
                    })
        
        # File analysis citations
        if file_results and file_results.get('search_results'):
            for result in file_results['search_results']:
                file_path = result.get('metadata', {}).get('file_path', 'Unknown file')
                citations.append({
                    'type': 'file',
                    'title': f"File: {os.path.basename(file_path)}",
                    'url': file_path,
                    'snippet': result.get('content', '')[:100] + '...' if len(result.get('content', '')) > 100 else result.get('content', '')
                })
        
        return citations
    
    def _simple_text_synthesis(self, query: str, context: str) -> str:
        """
        Simple text synthesis when LLM is not available
        
        Args:
            query: Original user query
            context: Combined context from agents
            
        Returns:
            Simple synthesized response
        """
        # Extract key information from context
        lines = context.split('\n')
        key_info = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('===') and not line.startswith('Source:') and not line.startswith('URL:'):
                if len(line) > 20:  # Only include substantial lines
                    key_info.append(line)
        
        # Create a simple response
        if key_info:
            response = f"Based on the available information:\n\n"
            for i, info in enumerate(key_info[:5], 1):  # Limit to top 5 pieces of info
                response += f"{i}. {info}\n"
            
            if len(key_info) > 5:
                response += f"\n... and {len(key_info) - 5} more pieces of information."
        else:
            response = f"I found some information related to your query '{query}', but I'm unable to provide a detailed synthesis at the moment. The raw information is available in the context."
        
        return response
