@echo off
REM Streamlit launcher for Multi-Agent Query Router (Windows)

echo 🚀 Starting Multi-Agent Query Router Streamlit App
echo ==================================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is required but not installed.
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies if needed
echo 📚 Checking dependencies...
pip install streamlit plotly >nul 2>&1

REM Check for API key
if "%GOOGLE_API_KEY%"=="" (
    echo ⚠️  Warning: GOOGLE_API_KEY environment variable not set
    echo The system will work with limited functionality
    echo.
)

echo 🌐 Starting Streamlit server...
echo 📱 The app will open in your browser automatically
echo 🔗 Manual access: http://localhost:8501
echo ⏹️  Press Ctrl+C to stop the server
echo.

REM Run Streamlit
python -m streamlit run streamlit_app.py --server.port 8501 --server.address localhost --browser.gatherUsageStats false

pause
