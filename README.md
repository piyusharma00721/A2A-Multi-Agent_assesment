# Multi-Agent Intelligent Assistant

[![Streamlit](https://img.shields.io/badge/Streamlit-FF6B35?logo=streamlit&logoColor=white)](https://streamlit.io/) [![LangChain](https://img.shields.io/badge/LangChain-8E44AD?logo=langchain&logoColor=white)](https://langchain.com/) [![Gemini](https://img.shields.io/badge/Gemini-4285F4?logo=google&logoColor=white)](https://ai.google.dev/) [![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)](https://python.org/)

A multi-agent system built with Streamlit, LangChain, and LangGraph for intelligent query routing between web search and file analysis agents. Powered by Google Gemini for LLM tasks, with robust vector stores for RAG (Retrieval-Augmented Generation) on uploaded files like PDFs and images.

This project demonstrates a production-ready prototype for handling diverse user queries: factual web searches (e.g., "Who won the last Champions Trophy?") and file-based Q&A (e.g., "Summarize this resume").

## Features
- **Query Routing**: LLM-based router (Gemini) classifies queries to web search or file analysis.
- **Web Search Agent**: Multi-backend support (Serper for Google SERP, Wikipedia API, DuckDuckGo) with LLM-parsed crawling fallback for robust results.
- **File Analysis Agent**: RAG with Hugging Face embeddings (free, local) and RetrievalQA chain for PDFs, TXT, CSV, images (with multi-modal Gemini for images).
- **Streamlit UI**: Chat interface with sidebar for recent chats/files, drag-and-drop upload, and real-time status.
- **Logging & Debugging**: Detailed step-by-step logs in terminal (`logs/assistant_YYYYMMDD.log`).
- **Modular Design**: Easy to extend agents/backends; session-based state for multi-turn chats.

## Quick Start
1. Clone the repo: `git clone https://github.com/piyusharma00721/A2A-Multi-Agent_assesment.git`
2. Install dependencies: `pip install -r requirements.txt`
3. Set up `.env`: Copy `.env.example` to `.env` and add your `GOOGLE_API_KEY` (from [Google AI Studio](https://aistudio.google.com/app/apikey)).
4. Run: `streamlit run app.py`
5. Open [http://localhost:8501](http://localhost:8501) and test queries!

## Installation
### Prerequisites
- Python 3.10+ (recommended: 3.11 for performance).
- Git for cloning.

### Steps
1. **Clone Repository**:
   ```
   git clone https://github.com/piyusharma00721/A2A-Multi-Agent_assesment.git
   cd A2A-Multi-Agent_assesment
   ```

2. **Create Virtual Environment** (recommended):
   ```
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```
   pip install -r requirements.txt
   ```

4. **System Dependencies for PDF Processing**:
   - **poppler-utils**: For PDF text extraction.
     - Windows: Download from [poppler-windows](https://github.com/oschwartz10612/poppler-windows/releases), extract, add `bin/` to PATH.
     - macOS: `brew install poppler`
     - Linux: `sudo apt install poppler-utils`
   - **Tesseract OCR** (for scanned PDFs): 
     - Windows: Install from [Tesseract at UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki), add to PATH.
     - macOS: `brew install tesseract`
     - Linux: `sudo apt install tesseract-ocr`

5. **Optional API Keys for Enhanced Search**:
   - `SERPER_API_KEY`: Free Google SERP fallback (2,500/month) from [serper.dev](https://serper.dev). Add to `.env`.

### Environment Variables
Create `.env` in the root directory:
```
GOOGLE_API_KEY=your_gemini_api_key_here  # Required for Gemini LLM
SERPER_API_KEY=your_serper_key_here      # Optional for Google search fallback
```
- Load with `python-dotenv` (automatic in code).
- **Security**: Add `.env` to `.gitignore`.

## Usage
1. **Launch UI**: `streamlit run app.py`
2. **Web Search**: Type "who won the last champions trophy?" → Routes to web agent, returns "India (2025)" via Serper/Wikipedia.
3. **File Analysis**:
   - Upload PDF/TXT/CSV/image via drag-and-drop.
   - Query "how many total experience does the candidate have?" → Routes to file agent, uses RAG to summarize from resume.
4. **Sidebar**: View/manage recent chats and uploaded files (with remove button).
5. **Logs**: Check terminal or `logs/assistant_YYYYMMDD.log` for debugging (e.g., routing decisions).

### Example Queries
- **Web**: "What is the current weather in Tokyo?" (crawls weather.com, parses with Gemini).
- **File**: Upload resume PDF + "Summarize Piyush's skills" (retrieves chunks, generates cited response).

## Project Structure
```
A2A-Multi-Agent_assesment/
├── app.py                          # Streamlit UI entry point
├── requirements.txt                # Dependencies
├── .env.example                    # Template for env vars
├── .gitignore                      # Ignore .env, logs, etc.
├── orchestrator/
│   └── graph.py                    # LangGraph workflow (routing + agents)
├── agents/
│   ├── router_agent.py             # LLM-based query classifier
│   ├── web_search_agent.py         # Multi-backend search + crawl
│   ├── file_analysis_agent.py      # RetrievalQA for file RAG
│   └── synthesizer_agent.py        # Final response synthesis
└── utils/
    ├── logger.py                   # Custom logging
    └── vector_store.py             # FAISS + Hugging Face embeddings
```

## Troubleshooting
- **API Key Error**: Ensure `GOOGLE_API_KEY` in `.env` and `load_dotenv()` called early (in `graph.py`).
- **PDF Upload Fails ("poppler not found")**: Install poppler-utils and add to PATH; restart terminal.
- **Scanned PDF (0 docs extracted)**: Install Tesseract OCR; code falls back automatically.
- **Web Search Rate Limit**: Use Serper key for better reliability; wait 1-2 mins for DDG resets.
- **Import Errors**: Run `pip install -r requirements.txt --upgrade`; check versions.
- **No Vector Store**: Re-upload file; check logs for extraction count (e.g., "Loaded 0 docs" means scanned PDF).

For issues, check logs or open an issue on GitHub.

## Contributing
1. Fork the repo.
2. Create a branch: `git checkout -b feature-branch`.
3. Commit changes: `git commit -m "Add feature"`.
4. Push: `git push origin feature-branch`.
5. Open a Pull Request.

Contributions welcome! Focus on new agents, UI enhancements, or backend integrations.

## License
MIT License. See [LICENSE](LICENSE) for details.

---

*Built with ❤️ by Piyush Sharma. Questions? [Open an issue](https://github.com/piyusharma00721/A2A-Multi-Agent_assesment/issues).*