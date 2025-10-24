import logging
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI  # Correct Gemini LLM import
from utils.vector_store import VectorStoreManager  # Correct import for your project
from utils.logger import log_step  # Assuming this is your logging utility
import os

logger = logging.getLogger(__name__)

class FileAnalysisAgent:
    def __init__(self, api_key: str = None, model_name: str = "gemini-2.5-flash", retrieval_k: int = 4):
        """
        Initialize the FileAnalysisAgent with RetrievalQA chain.
        
        Args:
            api_key (str, optional): Google API key for Gemini. Falls back to env var.
            model_name (str): Gemini model to use (default: gemini-2.5-flash).
            retrieval_k (int): Number of docs to retrieve (default: 4).
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found. Set it in .env or pass as api_key.")
        
        self.retrieval_k = retrieval_k
        self.vector_manager = VectorStoreManager()
        
        # Initialize LLM with Gemini
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=0,
            google_api_key=self.api_key
        )
        
        # Optional: Uncomment for local Mistral fallback (requires transformers, torch)
        # try:
        #     from langchain_huggingface import HuggingFacePipeline
        #     from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
        #     model_id = "mistralai/Mistral-7B-Instruct-v0.1"
        #     tokenizer = AutoTokenizer.from_pretrained(model_id)
        #     model = AutoModelForCausalLM.from_pretrained(model_id, device_map="auto", torch_dtype="auto")
        #     pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, max_new_tokens=200)
        #     self.llm = HuggingFacePipeline(pipeline=pipe)
        # except Exception as e:
        #     logger.warning(f"Local Mistral fallback failed: {e}. Using Gemini.")
        
        # Advanced RAG prompt for precise, cited answers
        prompt_template = """
        Use the following context from the file to answer the question. If you don't know, say so. Cite sources with [page X] if available.
        Context: {context}
        Question: {question}
        Answer: """
        self.prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
        
        # Build RetrievalQA chain
        self._build_chain()

    def _build_chain(self):
        """Build or rebuild the RetrievalQA chain."""
        # Get retriever from vector store (assumes file is loaded)
        if not self.vector_manager.vector_stores:
            logger.warning("No vector stores available. Load a file first.")
            return
        
        # Use the last uploaded file's vector store for retrieval (customize as needed)
        file_name = list(self.vector_manager.vector_stores.keys())[-1] if self.vector_manager.vector_stores else None
        if not file_name:
            raise ValueError("No file loaded. Upload a file before analysis.")
        
        retriever = self.vector_manager.vector_stores[file_name].as_retriever(search_kwargs={"k": self.retrieval_k})
        
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": self.prompt}
        )
        log_step("FileAnalysisAgent._build_chain", f"Built RetrievalQA chain for file: {file_name}")

    def analyze(self, query: str) -> str:
        """
        Analyze the query using RAG (RetrievalQA).
        
        Args:
            query (str): The question to answer based on the uploaded file.
            
        Returns:
            str: Answer with citations from retrieved docs.
        """
        try:
            log_step("FileAnalysisAgent.analyze", f"Analyzing query: {query}")
            
            # Rebuild chain if needed (e.g., new file uploaded)
            if not hasattr(self, 'qa_chain') or not self.qa_chain:
                self._build_chain()
            
            result = self.qa_chain.invoke({"query": query})
            answer = result["result"]
            
            # Extract sources from retrieved docs (e.g., page metadata)
            sources = [doc.metadata.get("page", "Unknown") for doc in result["source_documents"]]
            log_step("FileAnalysisAgent.analyze", f"Retrieved sources: {sources}")
            
            return f"{answer}\n\nSources: {sources}"
            
        except Exception as e:
            logger.error(f"[FileAnalysisAgent.analyze] Error: {str(e)}")
            return f"Analysis failed: {str(e)}. Ensure a file is uploaded and embedded. Check logs for details."

    def reload_file(self, file_name: str, file_path: str = None):
        """Reload and re-embed a specific file to refresh the chain."""
        self.vector_manager.load_and_embed_file(file_path, file_name)
        self._build_chain()
        log_step("FileAnalysisAgent.reload_file", f"Reloaded and rebuilt chain for {file_name}")