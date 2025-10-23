from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain_community.document_loaders import WebBaseLoader
from utils.logger import log_step
import logging
import os
import time
import re
from typing import Optional, Dict

logger = logging.getLogger(__name__)

class WebSearchError(Exception):
    """Custom exception for web search failures."""
    pass

class WebSearchAgent:
    def __init__(self, api_key: Optional[str] = None, max_retries: int = 3, crawl_timeout: int = 10):
        """Initialize with configurable parameters.
        Args:
            api_key (str, optional): Google API key. Defaults to env var.
            max_retries (int): Max retry attempts for DDG searches.
            crawl_timeout (int): Timeout in seconds for web crawling.
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables.")
        
        self.max_retries = max_retries
        self.crawl_timeout = crawl_timeout
        self.search = DuckDuckGoSearchRun()
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0,
            google_api_key=self.api_key
        )
        self.prompt = ChatPromptTemplate.from_template(
            """Using the search results or crawled content: {results}
            Answer the query: {query}
            Be concise and accurate. For live data like weather, prioritize current details."""
        )
        self.chain = self.prompt | self.llm | StrOutputParser()
        # Configurable source domains for crawling
        self.crawl_sources = {
            "weather": ["weather.com", "accuweather.com"],
            "sports": ["espn.com", "bbc.com/sport"],
            "general": ["en.wikipedia.org"]
        }

    def _perform_ddg_search(self, query: str) -> str:
        """Perform DDG search with retry logic."""
        for attempt in range(self.max_retries):
            try:
                log_step("WebSearchAgent._perform_ddg_search", f"Attempt {attempt + 1}/{self.max_retries} for: {query}")
                results = self.search.run(query)
                if results and len(results.strip()) > 50:  # Quality check
                    log_step("WebSearchAgent._perform_ddg_search", "DDG search successful")
                    return results
                else:
                    raise WebSearchError("Empty or irrelevant DDG results")
            except WebSearchError as e:
                if attempt < self.max_retries - 1:
                    wait_time = (2 ** attempt) + 1  # Exponential backoff: 3s, 5s, 9s
                    log_step("WebSearchAgent._perform_ddg_search", f"Retrying due to: {str(e)}. Waiting {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    log_step("WebSearchAgent._perform_ddg_search", f"DDG failed after {self.max_retries} attempts: {str(e)}")
                    raise
            except Exception as e:
                log_step("WebSearchAgent._perform_ddg_search", f"Unexpected error: {str(e)}")
                raise WebSearchError(f"DDG search failed: {str(e)}")

    def _select_crawl_url(self, query: str) -> str:
        """Select an appropriate URL for crawling based on query context."""
        log_step("WebSearchAgent._select_crawl_url", f"Selecting URL for query: {query}")
        keywords = query.lower().split()
        if any(word in keywords for word in ["weather", "forecast"]):
            source_list = self.crawl_sources["weather"]
        elif any(word in keywords for word in ["sport", "fifa", "winner"]):
            source_list = self.crawl_sources["sports"]
        else:
            source_list = self.crawl_sources["general"]
        
        # Quick DDG search for URL
        try:
            url_query = f"{query} site:{' OR site:'.join(source_list)}"
            url_results = self.search.run(url_query, max_results=1)
            url_match = re.search(r'https?://[^\s<>"]+', url_results)
            return url_match.group(0) if url_match else f"https://{source_list[0]}/wiki/{query.replace(' ', '_')}"
        except Exception as e:
            log_step("WebSearchAgent._select_crawl_url", f"URL selection failed: {str(e)}")
            return f"https://{source_list[0]}/search?q={query.replace(' ', '+')}"

    def _crawl_content(self, url: str) -> str:
        """Crawl content from a given URL with timeout."""
        log_step("WebSearchAgent._crawl_content", f"Attempting to crawl: {url}")
        try:
            loader = WebBaseLoader(url)
            loader.requests_timeout = self.crawl_timeout
            docs = loader.load()
            if docs:
                content = docs[0].page_content[:2000]  # Truncate to avoid token limits
                log_step("WebSearchAgent._crawl_content", "Crawl successful")
                return f"Crawled from {url}: {content}"
            raise WebSearchError("No content extracted from crawl")
        except Exception as e:
            log_step("WebSearchAgent._crawl_content", f"Crawl failed: {str(e)}")
            raise WebSearchError(f"Crawl error for {url}: {str(e)}")

    def execute(self, query: str) -> str:
        """Execute the web search process with DDG and crawl fallback."""
        log_step("WebSearchAgent.execute", f"Starting search for: {query}")
        try:
            # Attempt DDG search first
            results = self._perform_ddg_search(query)
        except WebSearchError:
            # Fallback to crawling
            log_step("WebSearchAgent.execute", "Falling back to web crawl due to DDG failure")
            try:
                crawl_url = self._select_crawl_url(query)
                results = self._crawl_content(crawl_url)
            except WebSearchError as e:
                log_step("WebSearchAgent.execute", f"Crawl fallback failed: {str(e)}")
                results = f"Error: Could not retrieve data. Fallback suggestion: Check {crawl_url} manually."

        # Process with LLM
        answer = self.chain.invoke({"query": query, "results": results})
        log_step("WebSearchAgent.execute", f"Generated answer: {answer[:100]}...")
        return answer

    def update_crawl_sources(self, category: str, sources: list):
        """Update or add crawl source domains dynamically."""
        if category in self.crawl_sources:
            self.crawl_sources[category] = sources
        else:
            self.crawl_sources[category] = sources
        log_step("WebSearchAgent.update_crawl_sources", f"Updated sources for {category}: {sources}")