# PowerShell script to start Open WebUI for RAG KB
# This script starts Open WebUI service with proper configuration

param(
    [string]$Port = "8080",
    [switch]$NoBrowser = $false,
    [switch]$IntegrationMode = $false
)

Write-Host "Starting Open WebUI for RAG KB..." -ForegroundColor Green

# Check if Open WebUI is installed in Python 3.12
try {
    $result = py -3.12 -c "import open_webui" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Open WebUI found in Python 3.12" -ForegroundColor Green
    } else {
        throw "Not installed"
    }
} catch {
    Write-Host "Open WebUI not found in Python 3.12." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Installing Open WebUI..." -ForegroundColor Cyan
    try {
        py -3.12 -m pip install open-webui
        Write-Host "Open WebUI installed successfully" -ForegroundColor Green
    } catch {
        Write-Host "Failed to install Open WebUI" -ForegroundColor Red
        Write-Host ""
        Write-Host "Alternative options:" -ForegroundColor Yellow
        Write-Host "1. Use the document management UI directly: http://localhost:8000/docs/docs-ui" -ForegroundColor White
        Write-Host "2. Install Open WebUI manually: py -3.12 -m pip install open-webui" -ForegroundColor White
        Start-Sleep -Seconds 3
        Start-Process "http://localhost:8000/docs/docs-ui"
        exit 0
    }
}

# Check if Ollama is running
Write-Host "Checking Ollama service..." -ForegroundColor Yellow
try {
    $ollamaResponse = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -ErrorAction Stop
    Write-Host "Ollama is running" -ForegroundColor Green
} catch {
    Write-Host "Ollama is not running. Starting Ollama..." -ForegroundColor Yellow
    Start-Process ollama -ArgumentList 'serve' -NoNewWindow
    Start-Sleep -Seconds 5
    
    # Check again
    try {
        $ollamaResponse = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -ErrorAction Stop
        Write-Host "Ollama started successfully" -ForegroundColor Green
    } catch {
        Write-Host "Failed to start Ollama. Please start it manually: ollama serve" -ForegroundColor Red
        exit 1
    }
}

# Check if RAG KB API is running
Write-Host "Checking RAG KB API..." -ForegroundColor Yellow
try {
    $apiResponse = Invoke-RestMethod -Uri "http://localhost:8000/health" -ErrorAction Stop
    Write-Host "RAG KB API is running" -ForegroundColor Green
} catch {
    Write-Host "RAG KB API is not running. Please start it first: .\scripts\start.ps1" -ForegroundColor Yellow
    Write-Host "Continuing with Open WebUI startup anyway..." -ForegroundColor Cyan
}

# Start Open WebUI with Ollama configuration to avoid HuggingFace model download
Write-Host "Starting Open WebUI on port $Port with Ollama configuration..." -ForegroundColor Yellow
Write-Host "Using Python 3.12 for Open WebUI" -ForegroundColor Cyan

# Load environment variables from .env file
if (Test-Path ".env") {
    Get-Content ".env" | ForEach-Object {
        if ($_ -match '^([^#].+?)=(.+)$') {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            [Environment]::SetEnvironmentVariable($name, $value, "Process")
            Write-Host "Set env: $name = $value" -ForegroundColor DarkGray
        }
    }
}

# Set environment variables for Ollama embeddings
$env:RAG_EMBEDDING_ENGINE = "ollama"
$env:RAG_EMBEDDING_MODEL = "nomic-embed-text"
$env:RAG_EMBEDDING_FUNCTION = "false"

# Use Python 3.12 to run Open WebUI
$python312 = "py"
$envArgs = @(
    "-3.12",
    "-c",
    "from open_webui import serve; serve()"
)
$webui = Start-Process $python312 -ArgumentList $envArgs -PassThru

# Wait for Open WebUI to start
Write-Host "Waiting for Open WebUI to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Check if Open WebUI is accessible
try {
    $webuiResponse = Invoke-RestMethod -Uri "http://localhost:$Port" -ErrorAction Stop
    Write-Host "Open WebUI started successfully" -ForegroundColor Green
} catch {
    Write-Host "Open WebUI may still be starting. Check in a few seconds." -ForegroundColor Yellow
}

# Open browser if not disabled
if (-not $NoBrowser) {
    if ($IntegrationMode) {
        Write-Host "Opening RAG KB Integration interface in browser..." -ForegroundColor Yellow
        Start-Sleep -Seconds 2
        Start-Process "http://localhost:8000/rag-kb-integration"
    } else {
        Write-Host "Opening Open WebUI in browser..." -ForegroundColor Yellow
        Start-Sleep -Seconds 2
        Start-Process "http://localhost:$Port"
    }
}

Write-Host ""
Write-Host "Open WebUI started successfully!" -ForegroundColor Green
Write-Host "Open WebUI: http://localhost:$Port" -ForegroundColor Cyan
Write-Host "RAG KB API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "Document Management UI: http://localhost:8000/docs/docs-ui" -ForegroundColor Cyan
Write-Host "Complete Integration: http://localhost:8000/rag-kb-integration" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Enter to stop Open WebUI..." -ForegroundColor Yellow
Read-Host

# Stop Open WebUI
Write-Host "Stopping Open WebUI..." -ForegroundColor Yellow
if ($webui -and !$webui.HasExited) {
    Stop-Process -InputObject $webui -Force -ErrorAction SilentlyContinue
}
Write-Host "Open WebUI stopped." -ForegroundColor Green