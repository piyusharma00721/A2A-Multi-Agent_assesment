# Multi-Agent Query Router - Architecture Documentation

## System Overview

The Multi-Agent Query Router is an intelligent assistant system that employs a multi-agent architecture to handle diverse user queries. The system intelligently routes incoming queries to specialized agents and synthesizes coherent responses.

## High-Level Architecture

### Core Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Input    │───▶│   Router Node   │───▶│ Agent Selection │
│  (Query + Files)│    │   (Gemini LLM)  │    │   (WEB/FILE)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                       ┌─────────────────┐              │
                       │ Web Search Agent│◀─────────────┼─────────────┐
                       │ (DuckDuckGo API)│              │             │
                       └─────────────────┘              │             │
                                │                       │             │
                                ▼                       │             │
                       ┌─────────────────┐              │             │
                       │ File Analysis   │◀─────────────┘             │
                       │ Agent (RAG +    │                            │
                       │ Multi-Modal)    │                            │
                       └─────────────────┘                            │
                                │                                     │
                                ▼                                     │
                       ┌─────────────────┐                            │
                       │   Synthesizer   │◀───────────────────────────┘
                       │   (Gemini LLM)  │
                       └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │  Final Response │
                       │  + Citations    │
                       └─────────────────┘
```

### Component Responsibilities

#### 1. Router Node (Query Classification)
- **Technology**: Google Gemini Pro via LangChain
- **Purpose**: Classifies incoming queries and determines which agent(s) should handle them
- **Input**: User query + file presence indicator
- **Output**: Agent choice (WEB_SEARCH, FILE_ANALYSIS, BOTH) + reasoning
- **Fallback**: Rule-based classification when LLM fails

#### 2. Web Search Agent
- **Technology**: DuckDuckGo Search API
- **Purpose**: Retrieves current information from the internet
- **Capabilities**:
  - General web search
  - News search
  - Key information extraction
  - Source citation
- **Output**: Structured search results with metadata

#### 3. File Analysis Agent (Multi-Modal RAG)
- **Technology**: 
  - PyMuPDF for PDF processing
  - Tesseract OCR for image text extraction
  - Pandas for tabular data processing
  - FAISS for vector storage
  - HuggingFace embeddings
- **Supported Formats**: PDF, TXT, CSV, XLSX, Images (PNG, JPG, etc.)
- **Process**:
  1. Extract text from files
  2. Split into chunks
  3. Create embeddings
  4. Build FAISS vector store
  5. Perform similarity search
- **Output**: Relevant document chunks with similarity scores

#### 4. Synthesizer
- **Technology**: Google Gemini Pro via LangChain
- **Purpose**: Combines information from multiple agents into coherent responses
- **Features**:
  - Context formatting
  - Citation extraction
  - Confidence scoring
  - Error handling
- **Output**: Final answer with citations and confidence score

#### 5. Orchestrator (LangGraph)
- **Technology**: LangGraph for workflow orchestration
- **Purpose**: Manages the execution flow between components
- **Workflow States**:
  - Router → Agent Selection
  - Web Search → File Analysis (if BOTH)
  - File Analysis → Synthesizer
  - Synthesizer → Final Response
- **Features**:
  - Conditional routing
  - Error handling
  - State management

#### 6. Logging System
- **Technology**: JSON-based logging
- **Purpose**: Tracks requests, responses, and system metrics
- **Features**:
  - Request/response logging
  - Performance metrics
  - Error tracking
  - Statistics generation

## Data Flow

### 1. Query Processing Flow
```
User Query → Router → Agent Selection → Agent Execution → Synthesis → Response
```

### 2. Web Search Flow
```
Query → DuckDuckGo API → Results Processing → Key Extraction → Context Formatting
```

### 3. File Analysis Flow
```
Files → Text Extraction → Chunking → Embedding → Vector Store → Similarity Search
```

### 4. Synthesis Flow
```
Agent Results → Context Combination → LLM Processing → Response Generation → Citation Extraction
```

## Framework Justification

### LangChain
- **Why**: Provides unified interface for LLM interactions
- **Benefits**: 
  - Consistent API across different LLM providers
  - Built-in prompt templates and chains
  - Easy integration with vector stores

### LangGraph
- **Why**: Enables complex multi-agent workflows
- **Benefits**:
  - State management across agents
  - Conditional routing
  - Error handling and recovery
  - Visual workflow representation

### Google Gemini
- **Why**: High-quality reasoning and text generation
- **Benefits**:
  - Strong performance on classification tasks
  - Good synthesis capabilities
  - Cost-effective for POC

### DuckDuckGo Search
- **Why**: Privacy-focused, no API key required
- **Benefits**:
  - Easy integration
  - Good search quality
  - No rate limiting for POC

### FAISS
- **Why**: Efficient vector similarity search
- **Benefits**:
  - Fast similarity search
  - In-memory storage for POC
  - Easy integration with embeddings

### PyMuPDF + Tesseract
- **Why**: Comprehensive file processing capabilities
- **Benefits**:
  - PDF text extraction
  - OCR for images
  - Reliable text processing

## Configuration Management

### Environment Variables
- `GOOGLE_API_KEY`: Required for Gemini API access
- `MAX_SEARCH_RESULTS`: Configurable search result limit
- `CHUNK_SIZE`: Text chunking size for RAG
- `CHUNK_OVERLAP`: Overlap between chunks

### File Type Support
- **Text**: `.txt` files
- **PDF**: `.pdf` files with page-by-page extraction
- **Images**: `.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp` with OCR
- **Tabular**: `.csv`, `.xlsx`, `.xls` with data analysis

## Error Handling

### Router Errors
- LLM API failures → Fallback to rule-based classification
- Invalid responses → Default to WEB_SEARCH

### Agent Errors
- Web search failures → Error message in results
- File processing errors → Graceful degradation
- Vector store failures → Empty search results

### Synthesis Errors
- LLM failures → Error response with available context
- Missing context → Clear error message

## Performance Considerations

### Latency Targets
- Router classification: < 2 seconds
- Web search: < 5 seconds
- File processing: < 10 seconds (depending on file size)
- Synthesis: < 3 seconds
- Total end-to-end: < 15 seconds

### Scalability
- In-memory FAISS storage (suitable for POC)
- Stateless agent design
- Configurable chunk sizes
- File size limits (10MB default)

## Security Considerations

### API Key Management
- Environment variable storage
- No hardcoded credentials
- Template file for configuration

### File Processing
- File size limits
- Type validation
- Error isolation

### Data Privacy
- No persistent storage of user data
- Local processing of files
- Privacy-focused search engine

## Monitoring and Observability

### Logging
- Request/response logging
- Performance metrics
- Error tracking
- Agent usage statistics

### Metrics
- Success rates
- Processing times
- Agent selection distribution
- File type processing statistics

## Future Enhancements

### Short-term
- FastAPI web interface
- Batch processing capabilities
- Enhanced error recovery
- Performance optimization

### Long-term
- Distributed vector storage
- Advanced RAG techniques
- Multi-language support
- Real-time streaming responses
- Integration with external knowledge bases

