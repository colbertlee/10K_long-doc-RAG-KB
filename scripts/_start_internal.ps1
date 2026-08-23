# PowerShell startup script for RAG KB system
# This script starts the RAG KB API server and checks for dependencies

Write-Host "🚀 Starting RAG KB System..." -ForegroundColor Green

# Check if Python is installed
Write-Host "📋 Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.11+ and add it to PATH." -ForegroundColor Red
    exit 1
}

# Check if required directories exist
Write-Host "📁 Checking directory structure..." -ForegroundColor Yellow
$requiredDirs = @("data", "data/uploads", "data/users", "lightrag_db", "static")
foreach ($dir in $requiredDirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "✅ Created directory: $dir" -ForegroundColor Green
    } else {
        Write-Host "✅ Directory exists: $dir" -ForegroundColor Green
    }
}

# Check if Ollama is running
Write-Host "🔍 Checking Ollama service..." -ForegroundColor Yellow
try {
    $ollamaResponse = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -UseBasicParsing -TimeoutSec 2
    if ($ollamaResponse.StatusCode -eq 200) {
        Write-Host "✅ Ollama is running" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Ollama service responding but may have issues" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️ Ollama is not running. Please start Ollama first." -ForegroundColor Yellow
    Write-Host "   Download from: https://ollama.ai/" -ForegroundColor Cyan
    Write-Host "   Run: ollama serve" -ForegroundColor Cyan
}

# Check if virtual environment exists
Write-Host "🐍 Checking virtual environment..." -ForegroundColor Yellow
if (Test-Path ".venv") {
    Write-Host "✅ Virtual environment found" -ForegroundColor Green
    # Activate virtual environment
    & ".venv\Scripts\Activate.ps1"
} else {
    Write-Host "⚠️ No virtual environment found. Creating one..." -ForegroundColor Yellow
    python -m venv .venv
    & ".venv\Scripts\Activate.ps1"
    Write-Host "✅ Virtual environment created and activated" -ForegroundColor Green
    
    # Install dependencies
    Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
    pip install -e .[all]
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Dependencies installed successfully" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
        exit 1
    }
}

# Check if configuration file exists
Write-Host "⚙️  Checking configuration..." -ForegroundColor Yellow
if (Test-Path "configs\config.yaml") {
    Write-Host "✅ Configuration file found" -ForegroundColor Green
} else {
    Write-Host "⚠️ Configuration file not found. Copying example..." -ForegroundColor Yellow
    Copy-Item "configs\config.example.yaml" "configs\config.yaml"
    Write-Host "✅ Configuration file created from example" -ForegroundColor Green
}

# Start the FastAPI server
Write-Host "🌐 Starting FastAPI server..." -ForegroundColor Yellow
Write-Host "   API will be available at: http://localhost:8000" -ForegroundColor Cyan
Write-Host "   API docs at: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "   Document Management: http://localhost:8000/docs/docs-ui" -ForegroundColor Cyan
Write-Host "   Press Ctrl+C to stop the server" -ForegroundColor Yellow

try {
    python -m uvicorn src.rag_kb.api.main:app --host 0.0.0.0 --port 8000 --reload
} catch {
    Write-Host "❌ Failed to start server" -ForegroundColor Red
    Write-Host "   Error: $_" -ForegroundColor Red
    exit 1
}