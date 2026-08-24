@echo off
echo Starting RAG KB System...
echo Current directory: %CD%
set PYTHONPATH=src
echo PYTHONPATH set to: %PYTHONPATH%
echo.
echo Starting API server on http://localhost:8000
echo Press Ctrl+C to stop the server
echo.
python -m uvicorn rag_kb.api.main:app --host 0.0.0.0 --port 8000 --reload
pause