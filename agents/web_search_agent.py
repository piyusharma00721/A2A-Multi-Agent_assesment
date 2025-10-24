from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.utilities import WikipediaAPIWrapper, GoogleSerperAPIWrapper
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
import random  # For jitter
from bs4 import BeautifulSoup  # HTML cleaning

logger = logging.getLogger(__name__)

class SearchBackendError(Exception):
    """Custom exception for search backend failures."""
    pass

class SerperBackend:
    """Serper (Google SERP) backend - free tier: 2,500/month."""
    def __init__(self, api_key: str):
        self.search = GoogleSerperAPIWrapper(serper_api_key=api_key)

    def search(self, query: str) -> str:
        return self.search.run(query)

class WikipediaBackend:
    """Wikipedia API backend - completely free."""
    def __init__(self):
        self.search = WikipediaAPIWrapper()

    def search(self, query: str) -> str:
        return self.search.run(query)

class DuckDuckGoBackend:
    """DuckDuckGo backend."""
    def __init__(self):
        self.search = DuckDuckGoSearchRun()

    def search(self, query: str) -> str:
        return self.search.run(query)

class WebSearchAgent:
    def __init__(self, api_key: Optional[str] = None, max_retries: int = 3, crawl_timeout: int = 10):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found.")
        
        self.max_retries = max_retries
        self.crawl_timeout = crawl_timeout
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0,
            google_api_key=self.api_key
        )
        self.prompt = ChatPromptTemplate.from_template(
            """Using the search results or parsed content: {results}
            Answer the query: {query}
            Be concise and accurate."""
        )
        self.chain = self.prompt | self.llm | StrOutputParser()
        
        # Backends (priority: Serper > Wikipedia > DDG)
        self.backends = []
        if os.getenv("SERPER_API_KEY"):
            self.backends.append(SerperBackend(os.getenv("SERPER_API_KEY")))
        self.backends.append(WikipediaBackend())
        self.backends.append(DuckDuckGoBackend())
        
        # LLM parser for crawled content
        self.parse_prompt = ChatPromptTemplate.from_template(
            """Extract key facts relevant to '{query}' from this page content. Ignore ads, navigation, and irrelevant sections. Summarize concisely in bullet points.
            Content: {content}
            Relevant facts:"""
        )
        self.parse_chain = self.parse_prompt | self.llm | StrOutputParser()
        
        # Static crawl URLs for reliability
        self.crawl_sources = {
            "champions trophy": "https://en.wikipedia.org/wiki/List_of_ICC_Champions_Trophy_finals",
            "weather": "https://weather.com/weather/today/l/TOXX0034:1:TO",  # Tokyo; customize
            "general": "https://en.wikipedia.org/wiki/Main_Page"
        }

    def _perform_search(self, query: str) -> str:
        """Try backends with retries."""
        for backend in self.backends:
            backend_name = backend.__class__.__name__
            for attempt in range(self.max_retries):
                try:
                    log_step("WebSearchAgent._perform_search", f"{backend_name} attempt {attempt + 1} for: {query}")
                    results = backend.search(query)
                    if results and len(results.strip()) > 50:
                        log_step("WebSearchAgent._perform_search", f"{backend_name} succeeded")
                        return results
                    raise SearchBackendError("Short results")
                except SearchBackendError:
                    if attempt < self.max_retries - 1:
                        wait_time = (2 ** attempt) + random.uniform(0, 1)
                        time.sleep(wait_time)
                    continue
                except Exception as e:
                    log_step("WebSearchAgent._perform_search", f"{backend_name} error: {str(e)}")
                    continue
        raise SearchBackendError("All backends failed")

    def _select_crawl_url(self, query: str) -> str:
        """Select targeted URL."""
        keywords = query.lower()
        if "champions trophy" in keywords:
            return self.crawl_sources["champions trophy"]
        elif "weather" in keywords:
            return self.crawl_sources["weather"]
        else:
            return self.crawl_sources["general"]

    def _crawl_and_parse(self, url: str, query: str) -> str:
        """Crawl, clean, and parse with LLM."""
        log_step("WebSearchAgent._crawl_and_parse", f"Crawling {url}")
        try:
            loader = WebBaseLoader(url)
            loader.requests_timeout = self.crawl_timeout
            docs = loader.load()
            raw_content = docs[0].page_content if docs else ""
            
            # Clean with BeautifulSoup
            soup = BeautifulSoup(raw_content, 'html.parser')
            text_content = soup.get_text(separator=' ', strip=True)[:3000]
            
            if not text_content:
                raise SearchBackendError("No content")
            
            # LLM parse
            parsed = self.parse_chain.invoke({"query": query, "content": text_content})
            return f"Parsed crawl: {parsed}"
        except Exception as e:
            raise SearchBackendError(f"Crawl/parse failed: {str(e)}")

    def execute(self, query: str) -> str:
        log_step("WebSearchAgent.execute", f"Query: {query}")
        try:
            results = self._perform_search(query)
        except SearchBackendError:
            log_step("WebSearchAgent.execute", "Backends failed; crawling...")
            try:
                crawl_url = self._select_crawl_url(query)
                results = self._crawl_and_parse(crawl_url, query)
            except SearchBackendError as e:
                log_step("WebSearchAgent.execute", f"Fallback failed: {str(e)}")
                results = f"Unable to retrieve. Tip: Search '{query}' on Wikipedia."
        
        answer = self.chain.invoke({"query": query, "results": results})
        log_step("WebSearchAgent.execute", f"Answer: {answer[:100]}...")
        return answer