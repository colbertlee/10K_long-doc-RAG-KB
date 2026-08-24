# RAG KB Server Startup Script
Write-Host "🚀 Starting RAG KB System..." -ForegroundColor Green
Write-Host "📍 Current directory: $PWD" -ForegroundColor Cyan

# Set PYTHONPATH to include src directory
$env:PYTHONPATH = "src"
Write-Host "🐍 PYTHONPATH set to: $env:PYTHONPATH" -ForegroundColor Cyan

# Check Python version
Write-Host "📋 Python version:" -ForegroundColor Yellow
python --version

# Start the server
Write-Host "🌐 Starting API server on http://localhost:8000" -ForegroundColor Green
Write-Host "   Press Ctrl+C to stop the server" -ForegroundColor Yellow

python -m uvicorn rag_kb.api.main:app --host 0.0.0.0 --port 8000 --reload