# Multi-Agent Query Router (A2A Assessment)

A proof-of-concept multi-agent system that intelligently routes user queries to specialized agents for web search and file analysis, then synthesizes coherent responses.

## 🎯 Overview

This system demonstrates an intelligent assistant that can handle diverse information requests by employing a multi-agent architecture. It routes queries to appropriate specialized agents and synthesizes comprehensive answers.

## 🏗️ Architecture

### Core Components

- **Router Node**: Uses Google Gemini to classify queries and select appropriate agents
- **Web Search Agent**: Retrieves current information using DuckDuckGo API
- **File Analysis Agent**: Processes multi-modal files (PDF, images, spreadsheets) using RAG
- **Synthesizer**: Combines agent outputs into coherent responses
- **Orchestrator**: Manages workflow using LangGraph

### Technology Stack

- **LLM**: Google Gemini Pro
- **Orchestration**: LangGraph + LangChain
- **Search**: DuckDuckGo Search API
- **File Processing**: PyMuPDF, Tesseract OCR, Pandas
- **Vector Storage**: FAISS
- **Embeddings**: HuggingFace Sentence Transformers

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Google Gemini API key

### Installation

1. **Clone and setup**:
```bash
git clone <repository>
cd multi-agent-query-router
python setup.py
```

2. **Configure environment**:
```bash
cp .env.template .env
# Edit .env and add your GOOGLE_API_KEY
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

### Usage

#### Interactive Mode
```bash
python main.py --interactive
```

#### Single Query
```bash
python main.py "What is the capital of France?"
```

#### With Files
```bash
python main.py "Summarize this document" -f document.pdf
```

#### View Statistics
```bash
python main.py --stats
```

## 📋 Sample Queries

### Web Search Queries
- "What is the capital of France?"
- "Who won the last FIFA World Cup?"
- "What is the current weather in Tokyo?"

### File Analysis Queries
- "Summarize the key findings in this document: [PDF]"
- "Find all mentions of 'quantum computing' in this text file: [TXT]"
- "Describe the main subject in this image: [IMAGE]"

### Combined Queries
- "Compare this document with current news about the topic"
- "Find recent information about the subject in this file"

## 🔧 Configuration

### Environment Variables
```bash
GOOGLE_API_KEY=your_gemini_api_key_here
MAX_SEARCH_RESULTS=5
CHUNK_SIZE=1500
CHUNK_OVERLAP=200
```

### Supported File Types
- **Text**: `.txt`
- **PDF**: `.pdf`
- **Images**: `.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`
- **Spreadsheets**: `.csv`, `.xlsx`, `.xls`

## 📊 System Features

### Query Routing Intelligence
- LLM-based classification with fallback rules
- Handles web search, file analysis, and combined queries
- Explains routing decisions

### Web Search Capabilities
- General web search and news search
- Key information extraction
- Source citation and ranking

### Multi-Modal File Analysis
- Text extraction from various formats
- OCR for image processing
- RAG-based information retrieval
- Similarity search with FAISS

### Response Synthesis
- Context-aware response generation
- Citation extraction and formatting
- Confidence scoring
- Error handling and graceful degradation

### Logging and Monitoring
- JSON-based request/response logging
- Performance metrics tracking
- System statistics and analytics
- Error tracking and debugging

## 🧪 Testing

Run the test suite:
```bash
python tests/test_queries.py
```

Test coverage includes:
- Query classification accuracy
- Agent functionality
- File processing capabilities
- Response synthesis
- Error handling

## 📈 Performance Metrics

### Target Performance
- Router classification: < 2 seconds
- Web search: < 5 seconds
- File processing: < 10 seconds
- Total end-to-end: < 15 seconds

### Evaluation Criteria
- **Routing Accuracy**: ≥80% on test prompts
- **Answer Relevance**: Manual validation
- **Latency**: ≤10s end-to-end per query
- **Resilience**: Graceful error handling

## 🏛️ Project Structure

```
multi-agent-query-router/
├── agents/                 # Agent implementations
│   ├── router.py          # Query classification
│   ├── web_search_agent.py # Web search functionality
│   ├── file_analysis_agent.py # File processing & RAG
│   └── synthesizer.py     # Response synthesis
├── utils/                 # Utility modules
│   └── logger.py         # Logging system
├── tests/                # Test cases
│   └── test_queries.py   # Comprehensive tests
├── test_files/           # Sample files for testing
├── outputs/              # Logs and results
├── orchestrator.py       # LangGraph workflow
├── config.py            # Configuration management
├── main.py              # Main application interface
├── setup.py             # Setup script
└── requirements.txt     # Dependencies
```

## 🔍 Key Design Decisions

### 1. Multi-Agent Architecture
- **Rationale**: Specialized agents for different query types
- **Benefits**: Modularity, scalability, maintainability

### 2. LLM-Based Routing
- **Rationale**: Intelligent query classification
- **Benefits**: Handles complex routing scenarios, explainable decisions

### 3. RAG for File Analysis
- **Rationale**: Efficient information retrieval from documents
- **Benefits**: Semantic search, relevance ranking, context preservation

### 4. LangGraph Orchestration
- **Rationale**: Complex workflow management
- **Benefits**: State management, conditional routing, error handling

### 5. JSON Logging
- **Rationale**: Structured data for analysis
- **Benefits**: Easy parsing, debugging, performance monitoring

## 🚧 Limitations & Future Work

### Current Limitations
- In-memory vector storage (not persistent)
- Single-threaded processing
- Basic error recovery
- Limited file size (10MB max)

### Future Enhancements
- FastAPI web interface
- Distributed vector storage
- Advanced RAG techniques
- Real-time streaming
- Multi-language support
- Integration with knowledge bases

## 📝 License

This project is created for assessment purposes. Please ensure you have appropriate licenses for all dependencies and APIs used.

## 🤝 Contributing

This is an assessment project. For questions or issues, please refer to the documentation or create an issue in the repository.

---

**Note**: This is a proof-of-concept implementation focused on demonstrating architectural principles and technical capabilities rather than production-ready features.