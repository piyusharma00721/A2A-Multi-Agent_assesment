from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from utils.logger import log_step
import logging
import os

logger = logging.getLogger(__name__)

class RouterAgent:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables.")
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash", 
            temperature=0,
            google_api_key=api_key
        )
        self.prompt = ChatPromptTemplate.from_template(
            """Classify the query: {query}
            If it mentions a file, upload, or analysis of document/image, route to 'file_analysis'.
            Otherwise, route to 'web_search'.
            Respond with only: 'file_analysis' or 'web_search'."""
        )
        self.chain = self.prompt | self.llm | StrOutputParser()

    def route(self, query: str, has_file: bool = False) -> str:
        input_dict = {"query": query}
        if has_file:
            input_dict["query"] += " (with attached file)"
        route = self.chain.invoke(input_dict)
        log_step("RouterAgent.route", f"Query: {query}, Has file: {has_file}, Route: {route}")
        return route.strip().lower()