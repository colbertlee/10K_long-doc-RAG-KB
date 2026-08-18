@echo off
REM Batch file to start RAG KB system (for users who prefer cmd)

echo Starting RAG KB System...
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Please install Python 3.11+ and add to PATH.
    pause
    exit /b 1
)

echo Python found
echo.

REM Check directories
if not exist "data" mkdir data
if not exist "data\uploads" mkdir data\uploads
if not exist "data\users" mkdir data\users
if not exist "lightrag_db" mkdir lightrag_db
if not exist "static" mkdir static

echo Directory structure ready
echo.

REM Check virtual environment
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Check configuration
if not exist "configs\config.yaml" (
    echo Creating configuration file...
    copy configs\config.example.yaml configs\config.yaml
)

echo.
echo Starting FastAPI server...
echo API will be available at: http://localhost:8000
echo API docs at: http://localhost:8000/docs
echo Press Ctrl+C to stop
echo.

python -m uvicorn src.rag_kb.api.main:app --host 0.0.0.0 --port 8000 --reload

pause