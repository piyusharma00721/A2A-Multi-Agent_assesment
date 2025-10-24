import logging
from typing import List, Dict
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import (
    UnstructuredPDFLoader,
    PyPDFLoader,
    TextLoader,
    CSVLoader,
    UnstructuredImageLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from utils.logger import log_step
import os
import subprocess
try:
    import pytesseract
    from pdf2image import convert_from_path
    from PIL import Image
except ImportError:
    pytesseract = None
    convert_from_path = None
    Image = None

logger = logging.getLogger(__name__)

class VectorStoreManager:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.vector_stores = {}
        self.documents = {}
        self.fallback_texts = {}

    def _check_poppler(self) -> bool:
        """Check if poppler is installed and in PATH."""
        try:
            subprocess.run(["pdfinfo", "--version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            log_step("VectorStore._check_poppler", "poppler-utils not found in PATH")
            return False

    def _ocr_pdf(self, file_path: str) -> List[Document]:
        """Perform OCR on PDF if poppler fails and Tesseract is available."""
        if not pytesseract or not convert_from_path or not Image:
            raise ValueError("Tesseract, pdf2image, and PIL required for OCR. Install 'pytesseract', 'pdf2image', and 'pillow'.")
        
        log_step("VectorStore._ocr_pdf", f"Attempting OCR on {file_path}")
        try:
            images = convert_from_path(file_path)
            docs = []
            for i, image in enumerate(images):
                text = pytesseract.image_to_string(image)
                if text.strip():
                    docs.append(Document(page_content=text, metadata={"page": i}))
            log_step("VectorStore._ocr_pdf", f"Extracted {len(docs)} pages via OCR")
            return docs if docs else []
        except Exception as e:
            log_step("VectorStore._ocr_pdf", f"OCR failed: {str(e)}")
            raise ValueError(f"OCR failed for {file_path}: {str(e)}")

    def load_and_embed_file(self, file_path: str, file_name: str) -> bool:
        log_step("VectorStore.load_and_embed_file", f"Starting processing for {file_name}")
        
        try:
            if file_name.endswith('.pdf'):
                if self._check_poppler():
                    try:
                        loader = UnstructuredPDFLoader(file_path, mode="single")
                        log_step("VectorStore.load_and_embed_file", f"Using UnstructuredPDFLoader for {file_name}")
                    except Exception as e:
                        log_step("VectorStore.load_and_embed_file", f"UnstructuredPDFLoader failed: {str(e)}. Falling back to PyPDFLoader.")
                        loader = PyPDFLoader(file_path)
                else:
                    if pytesseract and convert_from_path and Image:
                        docs = self._ocr_pdf(file_path)
                        loader = None  # Use OCR docs directly
                    else:
                        raise ValueError("poppler not found and OCR not configured. Install poppler-utils or Tesseract/pdf2image.")
            elif file_name.endswith('.txt'):
                loader = TextLoader(file_path)
            elif file_name.endswith(('.csv', '.xlsx')):
                loader = CSVLoader(file_path)
            elif file_name.endswith(('.png', '.jpg', '.jpeg')):
                loader = UnstructuredImageLoader(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_name}")
            
            docs = loader.load() if loader else docs
            log_step("VectorStore.load_and_embed_file", f"Loader extracted {len(docs)} documents for {file_name}")
            
            if not docs:
                raise ValueError(f"No content extracted from {file_name}. If scanned PDF, ensure OCR is set up with Tesseract.")
            
            full_text = " ".join([doc.page_content for doc in docs])
            self.fallback_texts[file_name] = full_text
            log_step("VectorStore.load_and_embed_file", f"Stored full text ({len(full_text)} chars) for fallback")
            
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
            raise ValueError(f"Failed to load {file_name}: {str(e)}. Try a text-based file or install poppler/Tesseract for PDFs.")

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