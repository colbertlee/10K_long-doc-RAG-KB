@echo off
echo Starting RAG KB System (Direct Source Mode)...
set PYTHONPATH=src
python -m uvicorn rag_kb.api.main:app --host 0.0.0.0 --port 8000 --reload
pause