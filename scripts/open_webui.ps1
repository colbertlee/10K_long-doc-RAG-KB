# PowerShell script to start Open WebUI for RAG KB
# This script starts Open WebUI service with proper configuration

param(
    [string]$Port = "8080",
    [switch]$NoBrowser = $false
)

Write-Host "Starting Open WebUI for RAG KB..." -ForegroundColor Green

# Check if Open WebUI is installed
try {
    $openwebui = Get-Command open-webui -ErrorAction Stop
    Write-Host "Open WebUI found at: $($openwebui.Source)" -ForegroundColor Cyan
} catch {
    Write-Host "Open WebUI not found." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Open WebUI requires manual installation due to npm dependencies." -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Installation options:" -ForegroundColor Yellow
    Write-Host "1. Docker (Recommended):" -ForegroundColor White
    Write-Host "   docker run -d -p 8080:8080 -v open-webui:/app/backend/data ghcr.io/open-webui/open-webui:main" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. Manual installation:" -ForegroundColor White
    Write-Host "   Visit: https://docs.openwebui.com/getting-started/installation" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3. Skip Open WebUI:" -ForegroundColor White
    Write-Host "   Use the document management UI directly: http://localhost:8000/docs/docs-ui" -ForegroundColor Gray
    Write-Host ""
    Write-Host "For now, opening the document management UI instead..." -ForegroundColor Cyan
    Start-Sleep -Seconds 3
    Start-Process "http://localhost:8000/docs/docs-ui"
    exit 0
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
$envArgs = @(
    "serve",
    "--port", $Port,
    "--ollama-embedding-model", "nomic-embed-text",
    "--embedding-engine", "ollama"
)
$webui = Start-Process open-webui -ArgumentList $envArgs -PassThru

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
    Write-Host "Opening Open WebUI in browser..." -ForegroundColor Yellow
    Start-Sleep -Seconds 2
    Start-Process "http://localhost:$Port"
}

Write-Host ""
Write-Host "Open WebUI started successfully!" -ForegroundColor Green
Write-Host "Open WebUI: http://localhost:$Port" -ForegroundColor Cyan
Write-Host "RAG KB API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "Document Management UI: http://localhost:8000/docs/docs-ui" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Enter to stop Open WebUI..." -ForegroundColor Yellow
Read-Host

# Stop Open WebUI
Write-Host "Stopping Open WebUI..." -ForegroundColor Yellow
Stop-Process -InputObject $webui -Force -ErrorAction SilentlyContinue
Write-Host "Open WebUI stopped." -ForegroundColor Green