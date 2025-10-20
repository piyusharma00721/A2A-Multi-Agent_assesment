# 🔧 Installation Guide - Multi-Agent Query Router

## 🚨 Current Issues & Solutions

### Issue 1: LangChain Import Errors
**Problem**: `cannot import name 'ChatGoogleGenerativeAI' from 'langchain_community.chat_models'`

**Solution**:
```bash
pip install langchain-google-genai==0.0.6
```

### Issue 2: Missing Sentence Transformers
**Problem**: `Could not import sentence_transformers python package`

**Solution**:
```bash
pip install sentence-transformers==2.2.2
```

### Issue 3: DuckDuckGo Search Error
**Problem**: `Client.__init__() got an unexpected keyword argument 'proxies'`

**Solution**:
```bash
pip install duckduckgo-search==3.8.6
```

### Issue 4: Torch Warning
**Problem**: `Tried to instantiate class '__path__._path', but it does not exist!`

**Solution**: This is a harmless warning and can be ignored, or install a specific torch version:
```bash
pip install torch==2.0.1
```

## 🚀 Quick Fix Commands

### Option 1: Automated Fix
```bash
python fix_dependencies.py
```

### Option 2: Manual Installation
```bash
# Install all required packages
pip install -r requirements.txt

# Install additional packages
pip install langchain-google-genai==0.0.6
pip install sentence-transformers==2.2.2
pip install duckduckgo-search==3.8.6
pip install torch==2.0.1
```

### Option 3: Fresh Installation
```bash
# Create new virtual environment
python -m venv venv_new
source venv_new/bin/activate  # Linux/Mac
# or
venv_new\Scripts\activate  # Windows

# Install all packages
pip install -r requirements.txt
pip install langchain-google-genai==0.0.6
pip install sentence-transformers==2.2.2
pip install duckduckgo-search==3.8.6
```

## 🧪 Testing the Installation

### Test All Components
```bash
python test_web_search.py
```

### Test Imports Only
```bash
python test_imports.py
```

### Test Streamlit App
```bash
streamlit run streamlit_app.py
```

## 🔑 Environment Setup

### 1. Set API Key
```bash
# Create .env file
echo "GOOGLE_API_KEY=your_api_key_here" > .env

# Or set environment variable
export GOOGLE_API_KEY=your_api_key_here  # Linux/Mac
set GOOGLE_API_KEY=your_api_key_here     # Windows
```

### 2. Verify Configuration
```bash
python -c "from config import Config; print('Config valid:', Config.validate_config()['valid'])"
```

## 📋 Complete Installation Steps

### Step 1: Environment Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

### Step 2: Install Dependencies
```bash
# Install base requirements
pip install -r requirements.txt

# Install additional packages
pip install langchain-google-genai==0.0.6
pip install sentence-transformers==2.2.2
pip install duckduckgo-search==3.8.6
pip install torch==2.0.1
```

### Step 3: Set API Key
```bash
# Create .env file
echo "GOOGLE_API_KEY=your_api_key_here" > .env
```

### Step 4: Test Installation
```bash
# Test components
python test_web_search.py

# Test Streamlit app
streamlit run streamlit_app.py
```

## 🔍 Troubleshooting

### Common Issues

**1. Import Errors**
- Check Python version (3.8+ required)
- Verify virtual environment is activated
- Try reinstalling packages

**2. API Key Issues**
- Verify GOOGLE_API_KEY is set correctly
- Check .env file exists and has correct format
- Test API key with Google's API

**3. Search Errors**
- Check internet connection
- Verify DuckDuckGo search package version
- Try different search queries

**4. Streamlit Issues**
- Check Streamlit version compatibility
- Verify all dependencies are installed
- Check for port conflicts (8501)

### Debug Commands

```bash
# Check Python version
python --version

# Check installed packages
pip list | grep -E "(langchain|streamlit|duckduckgo|sentence)"

# Test specific imports
python -c "import langchain_google_genai; print('OK')"
python -c "import sentence_transformers; print('OK')"
python -c "import duckduckgo_search; print('OK')"

# Check environment variables
python -c "import os; print('API Key set:', bool(os.getenv('GOOGLE_API_KEY')))"
```

## 🎯 Expected Behavior After Fix

### Successful Installation Should Show:
```
✅ langchain_google_genai import successful
✅ sentence_transformers import successful
✅ DuckDuckGo import successful
✅ WebSearchAgent initialization successful
✅ All tests passed! The system should work correctly.
```

### Streamlit App Should:
- Start without errors
- Show system status as "Configuration Valid"
- Allow web search queries
- Process file uploads
- Display analytics dashboard

## 📞 Support

If you continue to have issues:

1. **Check the error messages** carefully
2. **Run the test scripts** to identify specific problems
3. **Verify your Python version** (3.8+ required)
4. **Check your internet connection** for web search
5. **Verify your API key** is valid and has proper permissions

## 🎉 Success!

Once all tests pass, you can:
- Run the Streamlit app: `streamlit run streamlit_app.py`
- Use the CLI: `python main.py --interactive`
- Upload files and ask questions through the web interface
- Monitor system performance through the analytics dashboard
