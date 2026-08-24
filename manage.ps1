# RAG KB 统一管理脚本
# 一站式启动、停止、升级、状态检查

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("start", "stop", "restart", "status", "upgrade", "install", "open", "help")]
    [string]$Action = "help",
    
    [Parameter(Mandatory=$false)]
    [switch]$NoBrowser = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$NoOpenWebUI = $false,
    
    [Parameter(Mandatory=$false)]
    [string]$TargetVersion = "latest",
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipBackup = $false
)

function Show-Help {
    Write-Host "🚀 RAG KB 统一管理脚本" -ForegroundColor Green
    Write-Host ""
    Write-Host "使用方法:" -ForegroundColor Cyan
    Write-Host "  .\manage.ps1 <action> [options]" -ForegroundColor White
    Write-Host ""
    Write-Host "可用操作:" -ForegroundColor Cyan
    Write-Host "  start   - 启动 RAG KB 系统" -ForegroundColor White
    Write-Host "  stop    - 停止 RAG KB 系统" -ForegroundColor White
    Write-Host "  restart - 重启 RAG KB 系统" -ForegroundColor White
    Write-Host "  status  - 查看系统状态" -ForegroundColor White
    Write-Host "  upgrade - 升级到最新版本" -ForegroundColor White
    Write-Host "  install - 首次安装系统" -ForegroundColor White
    Write-Host "  open    - 在浏览器中打开系统" -ForegroundColor White
    Write-Host "  help    - 显示此帮助信息" -ForegroundColor White
    Write-Host ""
    Write-Host "选项:" -ForegroundColor Cyan
    Write-Host "  -NoBrowser      - 启动时不自动打开浏览器" -ForegroundColor White
    Write-Host "  -NoOpenWebUI    - 启动时不启动Open WebUI" -ForegroundColor White
    Write-Host "  -TargetVersion  - 升级到指定版本" -ForegroundColor White
    Write-Host "  -SkipBackup     - 升级时不创建备份" -ForegroundColor White
    Write-Host ""
    Write-Host "示例:" -ForegroundColor Cyan
    Write-Host "  .\manage.ps1 start" -ForegroundColor White
    Write-Host "  .\manage.ps1 upgrade -TargetVersion v0.4.0" -ForegroundColor White
    Write-Host "  .\manage.ps1 status" -ForegroundColor White
}

function Get-ProcessId {
    param([string]$ProcessName)
    
    try {
        $process = Get-Process -Name $ProcessName -ErrorAction SilentlyContinue
        if ($process) {
            return $process.Id
        }
    } catch {
        return $null
    }
    return $null
}

function Stop-RAGKB {
    Write-Host "🛑 停止 RAG KB 系统..." -ForegroundColor Yellow
    
    # 停止 uvicorn 进程
    $uvicornPid = Get-ProcessId "python"
    if ($uvicornPid) {
        try {
            Get-Process -Id $uvicornPid -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*uvicorn*" } | Stop-Process -Force -ErrorAction SilentlyContinue
            Write-Host "✅ 已停止 API 服务器" -ForegroundColor Green
        } catch {
            Write-Host "⚠️  无法停止 API 服务器" -ForegroundColor Yellow
        }
    } else {
        Write-Host "⚠️  API 服务器未运行" -ForegroundColor Yellow
    }
    
    # 停止 Open WebUI 进程
    try {
        $webuiProcess = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*open-webui*" }
        if ($webuiProcess) {
            Stop-Process -Id $webuiProcess.Id -Force -ErrorAction SilentlyContinue
            Write-Host "✅ 已停止 Open WebUI" -ForegroundColor Green
        }
    } catch {
        # Open WebUI 可能未运行，忽略错误
    }
    
    Write-Host "✅ 系统已停止" -ForegroundColor Green
}

function Start-RAGKB {
    Write-Host "🚀 启动 RAG KB 系统..." -ForegroundColor Green
    
    # 检查 Python
    Write-Host "📋 检查 Python 安装..." -ForegroundColor Yellow
    try {
        $pythonVersion = python --version 2>&1
        Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green
    } catch {
        Write-Host "❌ Python 未安装。请安装 Python 3.11+" -ForegroundColor Red
        exit 1
    }
    
    # 检查目录结构
    Write-Host "📁 检查目录结构..." -ForegroundColor Yellow
    $requiredDirs = @("data", "data/uploads", "data/users", "lightrag_db", "static", "data/feedback")
    foreach ($dir in $requiredDirs) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-Host "✅ 创建目录: $dir" -ForegroundColor Green
        }
    }
    
    # 检查 Ollama
    Write-Host "🔍 检查 Ollama 服务..." -ForegroundColor Yellow
    try {
        $ollamaResponse = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -UseBasicParsing -TimeoutSec 2
        if ($ollamaResponse.StatusCode -eq 200) {
            Write-Host "✅ Ollama 服务运行中" -ForegroundColor Green
        } else {
            Write-Host "⚠️  Ollama 服务可能有问题" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "⚠️  Ollama 未运行。建议启动: ollama serve" -ForegroundColor Yellow
    }
    
    # 检查虚拟环境
    Write-Host "🐍 检查虚拟环境..." -ForegroundColor Yellow
    if (Test-Path ".venv") {
        Write-Host "✅ 虚拟环境存在" -ForegroundColor Green
        & ".venv\Scripts\Activate.ps1"
    } else {
        Write-Host "⚠️  虚拟环境不存在，使用系统 Python" -ForegroundColor Yellow
    }
    
    # 启动 API 服务器
    Write-Host "🌐 启动 API 服务器..." -ForegroundColor Yellow
    Write-Host "   API: http://localhost:8000" -ForegroundColor Cyan
    Write-Host "   对话界面: http://localhost:8000/chat-ui" -ForegroundColor Cyan
    Write-Host "   知识图谱: http://localhost:8000/graph-ui" -ForegroundColor Cyan
    Write-Host "   按 Ctrl+C 停止服务器" -ForegroundColor Yellow
    
    try {
        # Set PYTHONPATH to include src directory
        $env:PYTHONPATH = "src"
        python -m uvicorn rag_kb.api.main:app --host 0.0.0.0 --port 8000 --reload
    } catch {
        Write-Host "❌ 启动失败" -ForegroundColor Red
        exit 1
    }
}

function Get-SystemStatus {
    Write-Host "📊 RAG KB 系统状态" -ForegroundColor Green
    Write-Host ""
    
    # 检查 API 服务器
    Write-Host "🌐 API 服务器:" -ForegroundColor Yellow
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            $data = $response.Content | ConvertFrom-Json
            Write-Host "  ✅ 状态: $($data.status)" -ForegroundColor Green
            Write-Host "  📦 版本: $($data.version)" -ForegroundColor Cyan
            Write-Host "  🔧 Ollama: $($data.ollama_status)" -ForegroundColor Cyan
        } else {
            Write-Host "  ❌ API 服务器未响应" -ForegroundColor Red
        }
    } catch {
        Write-Host "  ❌ API 服务器未运行" -ForegroundColor Red
    }
    
    # 检查 Ollama
    Write-Host "🤖 Ollama 服务:" -ForegroundColor Yellow
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -UseBasicParsing -TimeoutSec 2
        if ($response.StatusCode -eq 200) {
            $data = $response.Content | ConvertFrom-Json
            $models = $data.models | ForEach-Object { $_.name }
            Write-Host "  ✅ 运行中" -ForegroundColor Green
            Write-Host "  📦 模型: $($models -join ', ')" -ForegroundColor Cyan
        } else {
            Write-Host "  ❌ 未运行" -ForegroundColor Red
        }
    } catch {
        Write-Host "  ❌ 未运行" -ForegroundColor Red
    }
    
    # 检查进程
    Write-Host "🔄 运行进程:" -ForegroundColor Yellow
    $uvicornProcess = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*uvicorn*" }
    if ($uvicornProcess) {
        Write-Host "  ✅ API 服务器 (PID: $($uvicornProcess.Id))" -ForegroundColor Green
    } else {
        Write-Host "  ❌ API 服务器未运行" -ForegroundColor Red
    }
    
    # 检查端口占用
    Write-Host "🔌 端口占用:" -ForegroundColor Yellow
    $port8000 = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
    if ($port8000) {
        Write-Host "  ✅ 端口 8000 被占用" -ForegroundColor Green
    } else {
        Write-Host "  ❌ 端口 8000 未被占用" -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host "💡 提示:" -ForegroundColor Cyan
    Write-Host "  使用 .\manage.ps1 start 启动系统" -ForegroundColor White
    Write-Host "  使用 .\manage.ps1 stop 停止系统" -ForegroundColor White
}

function Upgrade-System {
    Write-Host "🔄 升级 RAG KB 系统..." -ForegroundColor Green
    Write-Host "目标版本: $TargetVersion" -ForegroundColor Cyan
    
    # 检查是否在项目目录
    if (-not (Test-Path "pyproject.toml")) {
        Write-Host "❌ 错误: 请在项目根目录运行此脚本" -ForegroundColor Red
        exit 1
    }
    
    # 获取当前版本
    $currentVersion = (Select-String -Path "pyproject.toml" -Pattern 'version = "').Line -replace '.*version = "(.*)".*', '$1'
    Write-Host "当前版本: $currentVersion" -ForegroundColor Cyan
    
    # 停止运行中的服务
    Write-Host "🛑 停止运行中的服务..." -ForegroundColor Yellow
    Stop-RAGKB
    
    # 创建备份
    if (-not $SkipBackup) {
        Write-Host "💾 创建备份..." -ForegroundColor Yellow
        $backupDir = "backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
        New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
        
        Copy-Item "pyproject.toml" -Destination $backupDir
        Copy-Item "configs" -Destination $backupDir -Recurse -Force
        if (Test-Path "data") {
            Copy-Item "data" -Destination $backupDir -Recurse -Force
        }
        Write-Host "✅ 备份完成: $backupDir" -ForegroundColor Green
    }
    
    # 拉取最新代码
    Write-Host "📥 拉取最新代码..." -ForegroundColor Yellow
    try {
        git fetch origin
        git checkout master
        git pull origin master
        Write-Host "✅ 代码更新完成" -ForegroundColor Green
    } catch {
        Write-Host "❌ Git 操作失败" -ForegroundColor Red
        exit 1
    }
    
    # 切换到指定版本
    if ($TargetVersion -ne "latest" -and $TargetVersion -ne $currentVersion) {
        Write-Host "🏷️  切换到版本 $TargetVersion..." -ForegroundColor Yellow
        try {
            git checkout "v$TargetVersion"
            Write-Host "✅ 版本切换完成" -ForegroundColor Green
        } catch {
            Write-Host "❌ 版本切换失败" -ForegroundColor Red
            exit 1
        }
    }
    
    # 更新依赖
    Write-Host "📦 更新依赖..." -ForegroundColor Yellow
    try {
        pip install -e .[all]
        Write-Host "✅ 依赖更新完成" -ForegroundColor Green
    } catch {
        Write- "❌ 依赖更新失败" -ForegroundColor Red
        exit 1
    }
    
    # 重新读取版本
    $newVersion = (Select-String -Path "pyproject.toml" -Pattern 'version = "').Line -replace '.*version = "(.*)".*', '$1'
    Write-Host "更新后版本: $newVersion" -ForegroundColor Cyan
    
    Write-Host "✅ 升级完成！" -ForegroundColor Green
    Write-Host "💡 使用 .\manage.ps1 start 启动新版本" -ForegroundColor Cyan
}

function Install-System {
    Write-Host "📦 安装 RAG KB 系统..." -ForegroundColor Green
    
    # 检查 Python
    Write-Host "📋 检查 Python 版本..." -ForegroundColor Yellow
    try {
        $pythonVersion = python --version 2>&1
        Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green
        
        # 检查版本是否符合要求
        if ($pythonVersion -notmatch "3\.(11|12|13|14|15)") {
            Write-Host "⚠️  Python 版本可能不兼容，建议使用 3.11+" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "❌ Python 未安装。请安装 Python 3.11+" -ForegroundColor Red
        exit 1
    }
    
    # 创建虚拟环境
    Write-Host "🐍 创建虚拟环境..." -ForegroundColor Yellow
    if (-not (Test-Path ".venv")) {
        python -m venv .venv
        & ".venv\Scripts\Activate.ps1"
        Write-Host "✅ 虚拟环境创建完成" -ForegroundColor Green
    } else {
        Write-Host "✅ 虚拟环境已存在" -ForegroundColor Green
        & ".venv\Scripts\Activate.ps1"
    }
    
    # 安装依赖
    Write-Host "📦 安装依赖..." -ForegroundColor Yellow
    try {
        pip install -e .[all]
        Write-Host "✅ 依赖安装完成" -ForegroundColor Green
    } catch {
        Write-Host "❌ 依赖安装失败" -ForegroundColor Red
        exit 1
    }
    
    # 创建目录结构
    Write-Host "📁 创建目录结构..." -ForegroundColor Yellow
    $requiredDirs = @("data", "data/uploads", "data/users", "data/feedback", "lightrag_db", "static", "logs")
    foreach ($dir in $requiredDirs) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-Host "✅ 创建目录: $dir" -ForegroundColor Green
        }
    }
    
    # 复制配置文件
    Write-Host "⚙️  配置系统..." -ForegroundColor Yellow
    if (-not (Test-Path "configs\config.yaml")) {
        if (Test-Path "configs\config.example.yaml") {
            Copy-Item "configs\config.example.yaml" "configs\config.yaml"
            Write-Host "✅ 配置文件创建完成" -ForegroundColor Green
        } else {
            Write-Host "⚠️  配置示例文件不存在" -ForegroundColor Yellow
        }
    } else {
        Write-Host "✅ 配置文件已存在" -ForegroundColor Green
    }
    
    Write-Host "✅ 安装完成！" -ForegroundColor Green
    Write-Host "💡 使用 .\manage.ps1 start 启动系统" -ForegroundColor Cyan
}

function Open-Browser {
    Write-Host "🌐 在浏览器中打开系统..." -ForegroundColor Green
    
    # 检查服务器是否运行
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 2
        if ($response.StatusCode -eq 200) {
            $url = "http://localhost:8000/chat-ui"
            Write-Host "📱 打开: $url" -ForegroundColor Cyan
            Start-Process $url
        } else {
            Write-Host "❌ 服务器未运行，请先启动: .\manage.ps1 start" -ForegroundColor Red
        }
    } catch {
        Write-Host "❌ 服务器未运行，请先启动: .\manage.ps1 start" -ForegroundColor Red
    }
}

# 主逻辑
switch ($Action) {
    "start" {
        Start-RAGKB
    }
    "stop" {
        Stop-RAGKB
    }
    "restart" {
        Stop-RAGKB
        Start-Sleep -Seconds 2
        Start-RAGKB
    }
    "status" {
        Get-SystemStatus
    }
    "upgrade" {
        Upgrade-System
    }
    "install" {
        Install-System
    }
    "open" {
        Open-Browser
    }
    "help" {
        Show-Help
    }
    default {
        Show-Help
    }
}