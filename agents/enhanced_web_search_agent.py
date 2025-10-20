"""
Enhanced Web Search Agent with multiple search sources and robust fallback
"""

import time
import requests
from typing import List, Dict, Any, Optional
from urllib.parse import quote_plus
import json

class EnhancedWebSearchAgent:
    """Enhanced web search agent with multiple search sources and robust fallback"""
    
    def __init__(self, max_results: int = 5, config=None):
        self.max_results = max_results
        self.config = config
        self.search_sources = [
            self._search_duckduckgo,
            self._search_serpapi,
            self._search_brave,
            self._search_google_custom
        ]
        print(f"[INIT] Enhanced WebSearchAgent initialized with {len(self.search_sources)} search sources")
    
    def _search_duckduckgo(self, query: str) -> List[Dict[str, Any]]:
        """Search using DuckDuckGo API"""
        try:
            from langchain_community.tools import DuckDuckGoSearchResults
            search_tool = DuckDuckGoSearchResults()
            raw_results = search_tool.run(query)
            
            if isinstance(raw_results, str):
                results = [{"title": "Result", "snippet": raw_results, "url": ""}]
            elif isinstance(raw_results, list):
                results = raw_results
            else:
                results = [{"title": "Result", "snippet": str(raw_results), "url": ""}]
            
            return [
                {
                    "rank": i + 1,
                    "title": r.get("title", "No title"),
                    "url": r.get("link", r.get("url", "")),
                    "snippet": r.get("snippet", "No snippet available"),
                    "source": "duckduckgo",
                    "timestamp": time.time(),
                }
                for i, r in enumerate(results[:self.max_results])
            ]
        except Exception as e:
            print(f"[ERROR] DuckDuckGo search failed: {e}")
            return []
    
    def _search_serpapi(self, query: str) -> List[Dict[str, Any]]:
        """Search using SerpAPI (if API key available)"""
        try:
            if not hasattr(self.config, 'SERPAPI_API_KEY') or not self.config.SERPAPI_API_KEY:
                return []
            
            url = "https://serpapi.com/search"
            params = {
                'q': query,
                'api_key': self.config.SERPAPI_API_KEY,
                'engine': 'google',
                'num': self.max_results
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            results = []
            for i, result in enumerate(data.get('organic_results', [])[:self.max_results]):
                results.append({
                    "rank": i + 1,
                    "title": result.get("title", "No title"),
                    "url": result.get("link", ""),
                    "snippet": result.get("snippet", "No snippet available"),
                    "source": "serpapi",
                    "timestamp": time.time(),
                })
            
            return results
        except Exception as e:
            print(f"[ERROR] SerpAPI search failed: {e}")
            return []
    
    def _search_brave(self, query: str) -> List[Dict[str, Any]]:
        """Search using Brave Search API (if API key available)"""
        try:
            if not hasattr(self.config, 'BRAVE_API_KEY') or not self.config.BRAVE_API_KEY:
                return []
            
            url = "https://api.search.brave.com/res/v1/web/search"
            headers = {
                'X-Subscription-Token': self.config.BRAVE_API_KEY,
                'Accept': 'application/json'
            }
            params = {
                'q': query,
                'count': self.max_results
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            data = response.json()
            
            results = []
            for i, result in enumerate(data.get('web', {}).get('results', [])[:self.max_results]):
                results.append({
                    "rank": i + 1,
                    "title": result.get("title", "No title"),
                    "url": result.get("url", ""),
                    "snippet": result.get("description", "No snippet available"),
                    "source": "brave",
                    "timestamp": time.time(),
                })
            
            return results
        except Exception as e:
            print(f"[ERROR] Brave search failed: {e}")
            return []
    
    def _search_google_custom(self, query: str) -> List[Dict[str, Any]]:
        """Search using Google Custom Search API (if API key available)"""
        try:
            if not hasattr(self.config, 'GOOGLE_SEARCH_API_KEY') or not self.config.GOOGLE_SEARCH_API_KEY:
                return []
            if not hasattr(self.config, 'GOOGLE_SEARCH_ENGINE_ID') or not self.config.GOOGLE_SEARCH_ENGINE_ID:
                return []
            
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': self.config.GOOGLE_SEARCH_API_KEY,
                'cx': self.config.GOOGLE_SEARCH_ENGINE_ID,
                'q': query,
                'num': self.max_results
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            results = []
            for i, result in enumerate(data.get('items', [])[:self.max_results]):
                results.append({
                    "rank": i + 1,
                    "title": result.get("title", "No title"),
                    "url": result.get("link", ""),
                    "snippet": result.get("snippet", "No snippet available"),
                    "source": "google_custom",
                    "timestamp": time.time(),
                })
            
            return results
        except Exception as e:
            print(f"[ERROR] Google Custom Search failed: {e}")
            return []
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        """Search using multiple sources with fallback"""
        print(f"[INFO] Enhanced search for: {query}")
        
        all_results = []
        
        # Try each search source
        for i, search_func in enumerate(self.search_sources):
            try:
                print(f"[INFO] Trying search source {i+1}/{len(self.search_sources)}")
                results = search_func(query)
                if results:
                    all_results.extend(results)
                    print(f"[INFO] Found {len(results)} results from source {i+1}")
                    # If we have enough results, we can stop
                    if len(all_results) >= self.max_results:
                        break
            except Exception as e:
                print(f"[WARNING] Search source {i+1} failed: {e}")
                continue
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_results = []
        for result in all_results:
            url = result.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(result)
            elif not url:  # Include results without URLs
                unique_results.append(result)
        
        # Limit to max_results
        final_results = unique_results[:self.max_results]
        print(f"[INFO] Enhanced search completed: {len(final_results)} unique results")
        
        return final_results
    
    def extract_key_information(self, results: List[Dict[str, Any]], query: str) -> Dict[str, Any]:
        """Extract key information from search results"""
        if not results:
            return {"summary": "No search results found", "key_facts": [], "sources": [], "confidence": 0.0}

        key_facts, sources, all_snippets = [], [], []
        for result in results:
            if not result.get("error", False):
                sources.append({"title": result["title"], "url": result["url"], "rank": result["rank"]})
                all_snippets.append(result["snippet"])

        # Simple keyword-based ranking
        query_keywords = set(query.lower().split())
        relevant_snippets = []
        for snippet in all_snippets:
            snippet_lower = snippet.lower()
            keyword_matches = sum(1 for keyword in query_keywords if keyword in snippet_lower)
            if keyword_matches > 0:
                relevant_snippets.append({"snippet": snippet, "relevance_score": keyword_matches / len(query_keywords)})
        
        relevant_snippets.sort(key=lambda x: x["relevance_score"], reverse=True)
        ranked_snippets = [s["snippet"][:200] + "..." if len(s["snippet"]) > 200 else s["snippet"] for s in relevant_snippets[:3]]

        key_facts.extend(ranked_snippets)
        confidence = min(1.0, len(sources) / 3.0) if sources else 0.0
        return {"summary": f"Found {len(sources)} relevant sources for '{query}'", "key_facts": key_facts, "sources": sources, "confidence": confidence, "total_results": len(results)}

    def is_current_information_needed(self, query: str) -> bool:
        """Determine if the query requires current/updated information"""
        current_indicators = [
            'current', 'latest', 'recent', 'today', 'now', 'this year', '2024', '2025',
            'weather', 'news', 'stock', 'price', 'election', 'covid', 'pandemic',
            'breaking', 'update', 'just', 'happened', 'live', 'real-time'
        ]
        query_lower = query.lower()
        return any(indicator in query_lower for indicator in current_indicators)

    def process_query(self, query: str) -> Dict[str, Any]:
        """Process query with enhanced search capabilities"""
        print(f"[INFO] Enhanced processing query: {query}")
        
        # Always try web search first for better results
        print("[INFO] Using enhanced web search")
        results = self.search(query)
        extracted_info = self.extract_key_information(results, query)
        
        return {
            "query": query, 
            "search_type": "enhanced_web", 
            "results": results, 
            "extracted_info": extracted_info, 
            "agent_type": "enhanced_web_search", 
            "timestamp": time.time()
        }
