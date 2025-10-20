@echo off
REM Multi-Agent Query Router - Demo Runner (Windows)
REM This script sets up and runs the demo

echo 🤖 Multi-Agent Query Router - Demo Setup
echo ========================================

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

REM Install dependencies
echo 📚 Installing dependencies...
pip install -r requirements.txt

REM Check for API key
if "%GOOGLE_API_KEY%"=="" (
    echo ⚠️  Warning: GOOGLE_API_KEY environment variable not set
    echo Please set your Google Gemini API key:
    echo set GOOGLE_API_KEY=your_api_key_here
    echo.
    echo You can also create a .env file with:
    echo GOOGLE_API_KEY=your_api_key_here
    echo.
    set /p continue="Do you want to continue anyway? (y/n): "
    if /i not "%continue%"=="y" exit /b 1
)

REM Create necessary directories
echo 📁 Creating directories...
if not exist "data" mkdir data
if not exist "outputs" mkdir outputs
if not exist "logs" mkdir logs
if not exist "test_files" mkdir test_files

REM Initialize empty log file
echo [] > outputs\requests.json

echo.
echo 🚀 Starting demo...
echo ==================

REM Run the demo
python demo.py

echo.
echo ✅ Demo completed!
echo.
echo To run the full interactive mode:
echo python main.py --interactive
echo.
echo To view system statistics:
echo python main.py --stats
echo.
echo To run tests:
echo python tests\test_queries.py

pause

