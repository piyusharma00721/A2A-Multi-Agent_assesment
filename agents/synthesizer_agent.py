from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from utils.logger import log_step
import logging
import os

logger = logging.getLogger(__name__)

class SynthesizerAgent:
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
            """Synthesize a final, natural response for the user.
            Query: {query}
            Agent output: {agent_output}
            Route: {route}"""
        )
        self.chain = self.prompt | self.llm | StrOutputParser()

    def synthesize(self, query: str, agent_output: str, route: str) -> str:
        final = self.chain.invoke({"query": query, "agent_output": agent_output, "route": route})
        log_step("SynthesizerAgent.synthesize", f"Synthesized: {final[:100]}...")
        return final