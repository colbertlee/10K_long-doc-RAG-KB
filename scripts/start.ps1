# PowerShell startup script for RAG KB services
# Run in an elevated PowerShell after installing dependencies

param(
    [switch]$NoOpenWebUI = $false,
    [switch]$NoBrowser = $false
)

Write-Host "Starting RAG KB services..." -ForegroundColor Green

# Start Ollama
Write-Host "Starting Ollama..." -ForegroundColor Yellow
$ollama = Start-Process ollama -ArgumentList 'serve' -PassThru
Start-Sleep -Seconds 5

# Start FastAPI backend
Write-Host "Starting FastAPI backend..." -ForegroundColor Yellow
$backend = Start-Process python -ArgumentList '-m','uvicorn','rag_kb.api.main:app','--reload','--host','0.0.0.0','--port','8000' -PassThru
Start-Sleep -Seconds 3

# Start Open WebUI (if installed and not disabled)
if (-not $NoOpenWebUI) {
    Write-Host "Starting Open WebUI..." -ForegroundColor Yellow
    try {
        $webui = Start-Process open-webui -ArgumentList 'serve' -PassThru
        Write-Host "Open WebUI started successfully" -ForegroundColor Green
    } catch {
        Write-Host "Open WebUI not found. Skipping..." -ForegroundColor Yellow
        Write-Host "To start Open WebUI separately, run: .\scripts\open_webui.ps1" -ForegroundColor Cyan
        $webui = $null
    }
} else {
    Write-Host "Open WebUI disabled. To start separately, run: .\scripts\open_webui.ps1" -ForegroundColor Yellow
    $webui = $null
}

Write-Host "RAG KB services started." -ForegroundColor Green
Write-Host "FastAPI backend: http://localhost:8000" -ForegroundColor Cyan
Write-Host "API docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "Document Management UI: http://localhost:8000/docs/docs-ui" -ForegroundColor Cyan
if ($webui) {
    Write-Host "Open WebUI: http://localhost:8080" -ForegroundColor Cyan
}
Write-Host ""

# Open browser if not disabled
if (-not $NoBrowser) {
    Write-Host "Opening Document Management UI in browser..." -ForegroundColor Yellow
    Start-Sleep -Seconds 2
    Start-Process "http://localhost:8000/docs/docs-ui"
    Write-Host ""
}

Write-Host "Press Enter to stop all services..." -ForegroundColor Yellow
Read-Host

# Stop all services
Write-Host "Stopping services..." -ForegroundColor Yellow
Stop-Process -InputObject $ollama,$backend -Force -ErrorAction SilentlyContinue
if ($webui) {
    Stop-Process -InputObject $webui -Force -ErrorAction SilentlyContinue
}

Write-Host "All services stopped." -ForegroundColor Green