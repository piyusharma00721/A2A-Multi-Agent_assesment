"""
File Analysis Agent for processing multi-modal files with RAG capabilities
"""

import os
import time
import fitz  # PyMuPDF
import pandas as pd
import pytesseract
from PIL import Image
from typing import List, Dict, Any, Optional, Union
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from config import Config

class FileAnalysisAgent:
    """Agent specialized in analyzing multi-modal files using RAG"""
    
    def __init__(self):
        """Initialize the file analysis agent (lazy import/fallback)"""
        # Lazy import the embeddings. If unavailable, fall back to simple text search.
        try:
            from langchain_community.embeddings import HuggingFaceEmbeddings  # type: ignore
            from langchain.text_splitter import RecursiveCharacterTextSplitter  # type: ignore

            self.embedder = HuggingFaceEmbeddings(
                model_name=Config.EMBEDDING_MODEL
            )
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=Config.CHUNK_SIZE,
                chunk_overlap=Config.CHUNK_OVERLAP,
                length_function=len,
            )
            self.use_embeddings = True
        except Exception as e:
            # Import failed — do not raise here so module import succeeds.
            print(f"Warning: Embeddings unavailable ({e}). Falling back to simple text search.")
            self.embedder = None
            self.text_splitter = None
            self.use_embeddings = False
        
        self.vectorstore = None
        self.file_metadata = {}
    
    def extract_text_from_file(self, file_path: str) -> Dict[str, Any]:
        """
        Extract text content from various file types
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary with extracted text and metadata
        """
        if not os.path.exists(file_path):
            return {
                'text': '',
                'metadata': {'error': f'File not found: {file_path}'},
                'success': False
            }
        
        file_ext = os.path.splitext(file_path)[1].lower()
        file_size = os.path.getsize(file_path)
        
        # Check file size limit
        if file_size > Config.MAX_FILE_SIZE:
            return {
                'text': '',
                'metadata': {'error': f'File too large: {file_size} bytes (max: {Config.MAX_FILE_SIZE})'},
                'success': False
            }
        
        try:
            if file_ext == '.pdf':
                return self._extract_pdf_text(file_path)
            elif file_ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
                return self._extract_image_text(file_path)
            elif file_ext in ['.csv', '.xlsx', '.xls']:
                return self._extract_tabular_text(file_path)
            elif file_ext == '.txt':
                return self._extract_text_file(file_path)
            else:
                return {
                    'text': '',
                    'metadata': {'error': f'Unsupported file type: {file_ext}'},
                    'success': False
                }
                
        except Exception as e:
            return {
                'text': '',
                'metadata': {'error': f'Error processing file: {str(e)}'},
                'success': False
            }
    
    def _extract_pdf_text(self, file_path: str) -> Dict[str, Any]:
        """Extract text from PDF files"""
        try:
            doc = fitz.open(file_path)
            text_content = []
            page_count = len(doc)
            
            for page_num in range(page_count):
                page = doc.load_page(page_num)
                text = page.get_text("text")
                if text.strip():
                    text_content.append(f"Page {page_num + 1}:\n{text}")
            
            doc.close()
            
            full_text = "\n\n".join(text_content)
            
            return {
                'text': full_text,
                'metadata': {
                    'file_type': 'pdf',
                    'page_count': page_count,
                    'file_size': os.path.getsize(file_path),
                    'extraction_method': 'pymupdf'
                },
                'success': True
            }
            
        except Exception as e:
            return {
                'text': '',
                'metadata': {'error': f'PDF extraction failed: {str(e)}'},
                'success': False
            }
    
    def _extract_image_text(self, file_path: str) -> Dict[str, Any]:
        """Extract text from images using OCR"""
        try:
            image = Image.open(file_path)
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Extract text using OCR
            extracted_text = pytesseract.image_to_string(image)
            
            return {
                'text': extracted_text,
                'metadata': {
                    'file_type': 'image',
                    'image_size': image.size,
                    'image_mode': image.mode,
                    'file_size': os.path.getsize(file_path),
                    'extraction_method': 'tesseract_ocr'
                },
                'success': True
            }
            
        except Exception as e:
            return {
                'text': '',
                'metadata': {'error': f'Image OCR failed: {str(e)}'},
                'success': False
            }
    
    def _extract_tabular_text(self, file_path: str) -> Dict[str, Any]:
        """Extract text from CSV and Excel files"""
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.csv':
                df = pd.read_csv(file_path)
            else:  # .xlsx, .xls
                df = pd.read_excel(file_path)
            
            # Convert DataFrame to text representation
            text_content = []
            text_content.append(f"Data Summary:")
            text_content.append(f"Shape: {df.shape[0]} rows, {df.shape[1]} columns")
            text_content.append(f"Columns: {', '.join(df.columns.tolist())}")
            text_content.append("\nData Preview:")
            text_content.append(df.head(10).to_string())
            
            if len(df) > 10:
                text_content.append(f"\n... and {len(df) - 10} more rows")
            
            # Add basic statistics for numeric columns
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                text_content.append("\nBasic Statistics:")
                text_content.append(df[numeric_cols].describe().to_string())
            
            return {
                'text': "\n".join(text_content),
                'metadata': {
                    'file_type': 'tabular',
                    'rows': df.shape[0],
                    'columns': df.shape[1],
                    'column_names': df.columns.tolist(),
                    'file_size': os.path.getsize(file_path),
                    'extraction_method': 'pandas'
                },
                'success': True
            }
            
        except Exception as e:
            return {
                'text': '',
                'metadata': {'error': f'Tabular extraction failed: {str(e)}'},
                'success': False
            }
    
    def _extract_text_file(self, file_path: str) -> Dict[str, Any]:
        """Extract text from plain text files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text_content = f.read()
            
            return {
                'text': text_content,
                'metadata': {
                    'file_type': 'text',
                    'file_size': os.path.getsize(file_path),
                    'extraction_method': 'direct_read'
                },
                'success': True
            }
            
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    text_content = f.read()
                
                return {
                    'text': text_content,
                    'metadata': {
                        'file_type': 'text',
                        'file_size': os.path.getsize(file_path),
                        'extraction_method': 'direct_read_latin1'
                    },
                    'success': True
                }
            except Exception as e:
                return {
                    'text': '',
                    'metadata': {'error': f'Text file extraction failed: {str(e)}'},
                    'success': False
                }
    
    def build_vectorstore(self, texts: List[str], metadatas: List[Dict] = None) -> Any:
        """
        Build FAISS vector store from texts
        
        Args:
            texts: List of text chunks
            metadatas: List of metadata dictionaries
            
        Returns:
            FAISS vector store or simple text store
        """
        if not self.use_embeddings or self.embedder is None:
            # Fallback to simple text storage
            return self._build_simple_text_store(texts, metadatas)
        
        try:
            if metadatas is None:
                metadatas = [{}] * len(texts)
            
            # Create documents
            documents = [
                Document(page_content=text, metadata=metadata)
                for text, metadata in zip(texts, metadatas)
            ]
            
            # Build vector store
            from langchain_community.vectorstores import FAISS
            vectorstore = FAISS.from_documents(documents, self.embedder)
            
            return vectorstore
            
        except Exception as e:
            print(f"Error building vector store: {e}")
            return self._build_simple_text_store(texts, metadatas)
    
    def _build_simple_text_store(self, texts: List[str], metadatas: List[Dict] = None) -> Dict[str, Any]:
        """
        Build a simple text store when embeddings are not available
        
        Args:
            texts: List of text chunks
            metadatas: List of metadata dictionaries
            
        Returns:
            Simple text store dictionary
        """
        if metadatas is None:
            metadatas = [{}] * len(texts)
        
        return {
            'type': 'simple_text_store',
            'texts': texts,
            'metadatas': metadatas,
            'total_chunks': len(texts)
        }
    
    def search_documents(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """
        Search for relevant documents using vector similarity or simple text search
        
        Args:
            query: Search query
            k: Number of results to return
            
        Returns:
            List of relevant document chunks
        """
        if self.vectorstore is None:
            return []
        
        try:
            # Check if it's a simple text store
            if isinstance(self.vectorstore, dict) and self.vectorstore.get('type') == 'simple_text_store':
                return self._simple_text_search(query, k)
            
            # Perform similarity search
            docs = self.vectorstore.similarity_search_with_score(query, k=k)
            
            results = []
            for doc, score in docs:
                results.append({
                    'content': doc.page_content,
                    'metadata': doc.metadata,
                    'similarity_score': float(score),
                    'source': 'file_analysis'
                })
            
            return results
            
        except Exception as e:
            print(f"Error searching documents: {e}")
            return []
    
    def _simple_text_search(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """
        Simple text search when embeddings are not available
        
        Args:
            query: Search query
            k: Number of results to return
            
        Returns:
            List of relevant document chunks
        """
        if not isinstance(self.vectorstore, dict) or self.vectorstore.get('type') != 'simple_text_store':
            return []
        
        texts = self.vectorstore.get('texts', [])
        metadatas = self.vectorstore.get('metadatas', [])
        
        # Simple keyword matching
        query_words = set(query.lower().split())
        scored_chunks = []
        
        for i, text in enumerate(texts):
            text_lower = text.lower()
            # Count matching words
            matches = sum(1 for word in query_words if word in text_lower)
            if matches > 0:
                score = matches / len(query_words)  # Simple scoring
                scored_chunks.append({
                    'content': text,
                    'metadata': metadatas[i] if i < len(metadatas) else {},
                    'similarity_score': score,
                    'source': 'file_analysis'
                })
        
        # Sort by score and return top k
        scored_chunks.sort(key=lambda x: x['similarity_score'], reverse=True)
        return scored_chunks[:k]
    
    def process_files(self, file_paths: List[str], query: str = "") -> Dict[str, Any]:
        """
        Process multiple files and build searchable index
        
        Args:
            file_paths: List of file paths to process
            query: Optional query for immediate search
            
        Returns:
            Dictionary with processing results
        """
        all_texts = []
        all_metadatas = []
        processing_results = []
        
        print(f"Processing {len(file_paths)} files...")
        
        for file_path in file_paths:
            print(f"Processing: {file_path}")
            
            # Extract text from file
            extraction_result = self.extract_text_from_file(file_path)
            processing_results.append({
                'file_path': file_path,
                'success': extraction_result['success'],
                'metadata': extraction_result['metadata']
            })
            
            if extraction_result['success'] and extraction_result['text'].strip():
                # Split text into chunks
                if self.use_embeddings and self.text_splitter is not None:
                    chunks = self.text_splitter.split_text(extraction_result['text'])
                else:
                    # Simple chunking when text splitter is not available
                    text = extraction_result['text']
                    chunk_size = Config.CHUNK_SIZE
                    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
                
                # Add file metadata to each chunk
                for chunk in chunks:
                    all_texts.append(chunk)
                    chunk_metadata = extraction_result['metadata'].copy()
                    chunk_metadata['file_path'] = file_path
                    chunk_metadata['chunk_length'] = len(chunk)
                    all_metadatas.append(chunk_metadata)
        
        # Build vector store if we have texts
        if all_texts:
            print("Building vector store...")
            self.vectorstore = self.build_vectorstore(all_texts, all_metadatas)
            if isinstance(self.vectorstore, dict) and self.vectorstore.get('type') == 'simple_text_store':
                print(f"Simple text store built with {len(all_texts)} chunks")
            else:
                print(f"Vector store built with {len(all_texts)} chunks")
        else:
            print("No text content extracted from files")
            self.vectorstore = None
        
        # Perform search if query provided
        search_results = []
        if query and self.vectorstore:
            search_results = self.search_documents(query)
        
        return {
            'query': query,
            'files_processed': len(file_paths),
            'processing_results': processing_results,
            'total_chunks': len(all_texts),
            'vectorstore_built': self.vectorstore is not None,
            'vectorstore_type': 'simple_text_store' if isinstance(self.vectorstore, dict) and self.vectorstore.get('type') == 'simple_text_store' else 'faiss_vectorstore',
            'search_results': search_results,
            'agent_type': 'file_analysis',
            'timestamp': time.time()
        }
    
    def analyze_single_file(self, file_path: str, query: str = "") -> Dict[str, Any]:
        """
        Analyze a single file and optionally search for specific information
        
        Args:
            file_path: Path to the file
            query: Optional query for information extraction
            
        Returns:
            Analysis results
        """
        return self.process_files([file_path], query)

