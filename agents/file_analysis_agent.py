from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from utils.vector_store import VectorStoreManager
from utils.logger import log_step
import os
import logging

logger = logging.getLogger(__name__)

class FileAnalysisAgent:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables.")
        self.vector_manager = VectorStoreManager()
        self.text_llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash", 
            temperature=0,
            google_api_key=api_key
        )
        self.multi_llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=api_key
        )
        self.prompt = ChatPromptTemplate.from_template(
            """Using the context from the file: {context}
            Answer the query: {query}
            If image, describe visually."""
        )
        self.chain = self.prompt | self.text_llm | StrOutputParser()

    def execute(self, query: str, file_name: str, file_path: str = None) -> str:
        log_step("FileAnalysisAgent.execute", f"Analyzing {file_name} for: {query}")
        
        # Embed if not already (assume embedded on upload)
        if file_path and file_name not in self.vector_manager.vector_stores:
            self.vector_manager.load_and_embed_file(file_path, file_name)
        
        # Retrieve relevant docs
        docs = self.vector_manager.retrieve_relevant_docs(query, file_name)
        context = "\n".join([doc["content"] for doc in docs])
        
        # For images, use multi-modal if applicable
        if file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
            # Use raw genai for multi-modal upload (requires configure)
            import google.generativeai as genai
            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
            img = genai.upload_file(file_path)
            response = self.multi_llm.invoke([query, img])
            answer = response.content
        else:
            answer = self.chain.invoke({"query": query, "context": context})
        
        log_step("FileAnalysisAgent.execute", f"Generated answer: {answer[:100]}...")
        return str(answer)