import time
from typing import List, Dict, Any, Optional

# Optional embeddings
try:
    from sentence_transformers import SentenceTransformer, util
    EMBEDDINGS_AVAILABLE = True
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    model = None

try:
    from langchain_community.tools import DuckDuckGoSearchResults
except ImportError:
    raise ImportError("Please install langchain-community: pip install langchain-community")

# Gemini LLM interface using LangChain ChatGoogleGenerativeAI
class GeminiLLMInterface:
    def __init__(self, api_key: str, model_name: str):
        if not api_key:
            raise ValueError("Google API key not set")
        try:
            from langchain_community.chat_models import ChatGoogleGenerativeAI
        except ImportError:
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
            except ImportError:
                from langchain.chat_models import ChatGoogleGenerativeAI
        from langchain.schema import HumanMessage

        self.HumanMessage = HumanMessage
        self.llm = ChatGoogleGenerativeAI(model=model_name, google_api_key=api_key, temperature=0.1)

    def answer(self, query: str) -> Optional[str]:
        try:
            response = self.llm([self.HumanMessage(content=query)])
            return response.content.strip() if response else None
        except Exception as e:
            print(f"[ERROR] Gemini LLM failed: {e}")
            return None

class WebSearchAgent:
    def __init__(self, max_results: int = 5, max_retries: int = 3, initial_wait: int = 2, config=None):
        self.max_results = max_results
        self.max_retries = max_retries
        self.initial_wait = initial_wait
        self.search_tool = DuckDuckGoSearchResults()
        self.llm = GeminiLLMInterface(api_key=config.GOOGLE_API_KEY, model_name=config.GEMINI_MODEL)
        print(f"[INIT] WebSearchAgent initialized with max_results={max_results}, max_retries={max_retries}, initial_wait={initial_wait}")

    def search(self, query: str, max_results: Optional[int] = None) -> List[Dict[str, Any]]:
        """Search the web using DuckDuckGo with retry logic"""
        if max_results is None:
            max_results = self.max_results

        wait_time = self.initial_wait
        for attempt in range(1, self.max_retries + 1):
            try:
                print(f"[INFO] Searching web for: {query} (Attempt {attempt})")
                raw_results = self.search_tool.run(query)

                if isinstance(raw_results, str):
                    results = [{"title": "Result", "snippet": raw_results, "url": ""}]
                elif isinstance(raw_results, list):
                    results = raw_results
                else:
                    results = [{"title": "Result", "snippet": str(raw_results), "url": ""}]

                processed_results = [
                    {
                        "rank": i + 1,
                        "title": r.get("title", "No title"),
                        "url": r.get("link", r.get("url", "")),
                        "snippet": r.get("snippet", "No snippet available"),
                        "source": "web_search",
                        "timestamp": time.time(),
                    }
                    for i, r in enumerate(results[:max_results])
                ]
                print(f"[INFO] Found {len(processed_results)} web results.")
                return processed_results

            except Exception as e:
                msg = str(e).lower()
                if "202 ratelimit" in msg or "rate limit" in msg:
                    print(f"[WARNING] Rate-limited by DuckDuckGo. Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                    wait_time *= 2
                else:
                    print(f"[ERROR] Web search failed: {e}")
                    return [{"rank": 1, "title": "Search Error", "url": "", "snippet": f"Unable to perform web search: {e}", "source": "web_search", "timestamp": time.time(), "error": True}]

        return [{"rank": 1, "title": "Search Error", "url": "", "snippet": "Unable to perform web search after retries due to rate-limiting.", "source": "web_search", "timestamp": time.time(), "error": True}]

    def extract_key_information(self, results: List[Dict[str, Any]], query: str) -> Dict[str, Any]:
        """Extract key information from search results"""
        if not results:
            return {"summary": "No search results found", "key_facts": [], "sources": [], "confidence": 0.0}

        key_facts, sources, all_snippets = [], [], []
        for result in results:
            if not result.get("error", False):
                sources.append({"title": result["title"], "url": result["url"], "rank": result["rank"]})
                all_snippets.append(result["snippet"])

        if EMBEDDINGS_AVAILABLE and all_snippets:
            query_emb = model.encode([query], convert_to_tensor=True)
            snippet_embs = model.encode(all_snippets, convert_to_tensor=True)
            scores = util.cos_sim(query_emb, snippet_embs)[0]
            ranked_snippets = [all_snippets[i] for i in scores.argsort(descending=True)[:3]]
        else:
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
        """Process query with improved LLM-first approach and robust web search"""
        print(f"[INFO] Processing query: {query}")
        
        # Check if query needs current information
        needs_current_info = self.is_current_information_needed(query)
        
        # For general knowledge questions, try LLM first
        if not needs_current_info:
            print("[INFO] Trying LLM first for general knowledge question")
            try:
                llm_answer = self.llm.answer(query)
                if llm_answer and len(llm_answer.strip()) > 20:  # Ensure we got a substantial answer
                    print("[INFO] LLM provided satisfactory answer")
                    return {
                        "query": query, 
                        "search_type": "llm", 
                        "results": [], 
                        "extracted_info": {
                            "summary": "Answer retrieved from Gemini LLM", 
                            "key_facts": [llm_answer], 
                            "sources": [], 
                            "confidence": 0.9, 
                            "total_results": 0
                        }, 
                        "agent_type": "llm_first", 
                        "timestamp": time.time()
                    }
            except Exception as e:
                print(f"[WARNING] LLM failed: {e}")
        
        # Use web search for current information or if LLM failed
        print("[INFO] Using web search")
        try:
            results = self.search(query)
            if results and not all(r.get("error", False) for r in results):
                extracted_info = self.extract_key_information(results, query)
                return {
                    "query": query, 
                    "search_type": "web", 
                    "results": results, 
                    "extracted_info": extracted_info, 
                    "agent_type": "web_search", 
                    "timestamp": time.time()
                }
        except Exception as e:
            print(f"[WARNING] Web search failed: {e}")
        
        # Final fallback to LLM
        print("[INFO] Using LLM as final fallback")
        try:
            llm_answer = self.llm.answer(query)
            if llm_answer:
                return {
                    "query": query, 
                    "search_type": "llm_fallback", 
                    "results": [], 
                    "extracted_info": {
                        "summary": "Answer retrieved from Gemini LLM (web search failed)", 
                        "key_facts": [llm_answer], 
                        "sources": [], 
                        "confidence": 0.7, 
                        "total_results": 0
                    }, 
                    "agent_type": "llm_fallback", 
                    "timestamp": time.time()
                }
        except Exception as e:
            print(f"[ERROR] LLM fallback failed: {e}")
        
        # Ultimate fallback
        return {
            "query": query, 
            "search_type": "error", 
            "results": [], 
            "extracted_info": {
                "summary": "Unable to process query - all methods failed", 
                "key_facts": ["I apologize, but I'm unable to process your query at the moment. Please try again later."], 
                "sources": [], 
                "confidence": 0.0, 
                "total_results": 0
            }, 
            "agent_type": "error", 
            "timestamp": time.time()
        }
