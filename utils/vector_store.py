import logging
from typing import List, Dict
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import (
    UnstructuredPDFLoader,
    PyPDFLoader,  # Fallback
    TextLoader,
    CSVLoader,
    UnstructuredImageLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from utils.logger import log_step
import os

logger = logging.getLogger(__name__)

class VectorStoreManager:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.vector_stores = {}  # file_name -> FAISS index
        self.documents = {}  # file_name -> list of full doc contents
        self.fallback_texts = {}  # file_name -> full text for keyword fallback

    def load_and_embed_file(self, file_path: str, file_name: str) -> bool:
        log_step("VectorStore.load_and_embed_file", f"Starting processing for {file_name}")
        
        try:
            # Try UnstructuredPDFLoader first
            if file_name.endswith('.pdf'):
                try:
                    loader = UnstructuredPDFLoader(file_path, mode="single")
                    log_step("VectorStore.load_and_embed_file", f"Using UnstructuredPDFLoader for {file_name}")
                except ImportError as e:
                    log_step("VectorStore.load_and_embed_file", f"UnstructuredPDFLoader failed: {str(e)}. Falling back to PyPDFLoader.")
                    loader = PyPDFLoader(file_path)
            elif file_name.endswith('.txt'):
                loader = TextLoader(file_path)
            elif file_name.endswith(('.csv', '.xlsx')):
                loader = CSVLoader(file_path)
            elif file_name.endswith(('.png', '.jpg', '.jpeg')):
                loader = UnstructuredImageLoader(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_name}")
            
            docs = loader.load()
            log_step("VectorStore.load_and_embed_file", f"Loader extracted {len(docs)} documents for {file_name}")
            
            if not docs:
                raise ValueError(f"No content extracted from {file_name}. If scanned PDF, use OCR or text version.")
            
            # Store full text for fallback
            full_text = " ".join([doc.page_content for doc in docs])
            self.fallback_texts[file_name] = full_text
            log_step("VectorStore.load_and_embed_file", f"Stored full text ({len(full_text)} chars) for fallback")
            
            # Split and embed
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            splits = text_splitter.split_documents(docs)
            log_step("VectorStore.load_and_embed_file", f"Split into {len(splits)} chunks for {file_name}")
            
            if splits:
                vector_store = FAISS.from_documents(splits, self.embeddings)
                self.vector_stores[file_name] = vector_store
                self.documents[file_name] = splits
                log_step("VectorStore.load_and_embed_file", f"Successfully embedded and stored FAISS index for {file_name}")
                return True
            else:
                log_step("VectorStore.load_and_embed_file", f"No splits generated; using full-text fallback only for {file_name}")
                return True
                
        except Exception as e:
            log_step("VectorStore.load_and_embed_file", f"ERROR processing {file_name}: {str(e)}")
            raise ValueError(f"Failed to load {file_name}: {str(e)}. Try a text-based file for testing.")

    def retrieve_relevant_docs(self, query: str, file_name: str, k: int = 4) -> List[Dict]:
        log_step("VectorStore.retrieve_relevant_docs", f"Retrieving for query '{query}' from {file_name}")
        
        if file_name not in self.vector_stores and file_name not in self.fallback_texts:
            raise ValueError(f"No data stored for {file_name}—re-upload the file.")
        
        try:
            if file_name in self.vector_stores:
                retriever = self.vector_stores[file_name].as_retriever(search_kwargs={"k": k})
                docs = retriever.invoke(query)
                log_step("VectorStore.retrieve_relevant_docs", f"Retrieved {len(docs)} semantic docs from {file_name}")
            else:
                full_text = self.fallback_texts[file_name]
                sentences = full_text.split('. ')
                relevant = [s for s in sentences if any(word.lower() in s.lower() for word in query.split())][:k]
                docs = [Document(page_content=' '.join(relevant), metadata={"source": "fallback"})]
                log_step("VectorStore.retrieve_relevant_docs", f"Retrieved {len(docs)} keyword-matched docs from {file_name}")
            
            return [{"content": doc.page_content, "metadata": doc.metadata} for doc in docs]
        except Exception as e:
            log_step("VectorStore.retrieve_relevant_docs", f"Retrieval error for {file_name}: {str(e)}")
            raise ValueError(f"Retrieval failed for {file_name}: {str(e)}")

    def remove_file(self, file_name: str):
        self.vector_stores.pop(file_name, None)
        self.documents.pop(file_name, None)
        self.fallback_texts.pop(file_name, None)
        log_step("VectorStore.remove_file", f"Removed all data for {file_name}")