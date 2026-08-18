# Installation script for RAG KB system
# This script sets up the environment and installs dependencies

Write-Host "🔧 RAG KB Installation Script" -ForegroundColor Green
Write-Host "=============================" -ForegroundColor Green

# Check Python version
Write-Host "📋 Checking Python version..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python version: $pythonVersion" -ForegroundColor Green
    
    # Check if version is 3.11+
    $versionMatch = $pythonVersion -match "Python (\d+)\.(\d+)"
    if ($versionMatch) {
        $major = [int]$matches[1]
        $minor = [int]$matches[2]
        if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 11)) {
            Write-Host "❌ Python 3.11+ required. Current version: $pythonVersion" -ForegroundColor Red
            exit 1
        }
    }
} catch {
    Write-Host "❌ Python not found. Please install Python 3.11+ from https://www.python.org/" -ForegroundColor Red
    exit 1
}

# Create virtual environment
Write-Host "🐍 Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path ".venv") {
    Write-Host "⚠️ Virtual environment already exists. Removing old one..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force .venv
}

python -m venv .venv
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Virtual environment created" -ForegroundColor Green

# Activate virtual environment
Write-Host "🔄 Activating virtual environment..." -ForegroundColor Yellow
& ".venv\Scripts\Activate.ps1"

# Upgrade pip
Write-Host "📦 Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install package in development mode
Write-Host "📦 Installing RAG KB package..." -ForegroundColor Yellow
pip install -e .[all]
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install package" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Package installed successfully" -ForegroundColor Green

# Create required directories
Write-Host "📁 Creating directory structure..." -ForegroundColor Yellow
$requiredDirs = @("data", "data/uploads", "data/users", "data/bm25_cache", "lightrag_db", "static", "logs")
foreach ($dir in $requiredDirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "✅ Created directory: $dir" -ForegroundColor Green
    }
}

# Copy configuration file
Write-Host "⚙️  Setting up configuration..." -ForegroundColor Yellow
if (Test-Path "configs\config.example.yaml") {
    if (-not (Test-Path "configs\config.yaml")) {
        Copy-Item "configs\config.example.yaml" "configs\config.yaml"
        Write-Host "✅ Configuration file created" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Configuration file already exists" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ Configuration example file not found" -ForegroundColor Red
}

# Check Ollama installation
Write-Host "🔍 Checking Ollama installation..." -ForegroundColor Yellow
try {
    $ollamaVersion = ollama --version 2>&1
    Write-Host "✅ Ollama found: $ollamaVersion" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Ollama not found. Please install from https://ollama.ai/" -ForegroundColor Yellow
    Write-Host "   After installation, run: ollama serve" -ForegroundColor Cyan
}

# Download required Ollama models
Write-Host "🤖 Checking Ollama models..." -ForegroundColor Yellow
try {
    $models = ollama list 2>&1
    $hasEmbedding = $models -match "nomic-embed-text"
    $hasLLM = $models -match "qwen3.5"
    
    if (-not $hasEmbedding) {
        Write-Host "📥 Downloading embedding model (nomic-embed-text)..." -ForegroundColor Yellow
        ollama pull nomic-embed-text
    } else {
        Write-Host "✅ Embedding model already installed" -ForegroundColor Green
    }
    
    if (-not $hasLLM) {
        Write-Host "📥 Downloading LLM model (qwen3.5:4b)..." -ForegroundColor Yellow
        ollama pull qwen3.5:4b
    } else {
        Write-Host "✅ LLM model already installed" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️ Could not check/download Ollama models. Please run manually:" -ForegroundColor Yellow
    Write-Host "   ollama pull nomic-embed-text" -ForegroundColor Cyan
    Write-Host "   ollama pull qwen3.5:4b" -ForegroundColor Cyan
}

# Run tests
Write-Host "🧪 Running tests..." -ForegroundColor Yellow
pytest tests/ -v
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ All tests passed" -ForegroundColor Green
} else {
    Write-Host "⚠️ Some tests failed. Check the output above." -ForegroundColor Yellow
}

Write-Host "🎉 Installation completed successfully!" -ForegroundColor Green
Write-Host "=============================" -ForegroundColor Green
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Start Ollama: ollama serve" -ForegroundColor White
Write-Host "2. Start the server: .\scripts\start.ps1" -ForegroundColor White
Write-Host "3. Open browser: http://localhost:8000/docs" -ForegroundColor White