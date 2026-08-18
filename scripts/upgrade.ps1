# PowerShell automatic upgrade script for RAG KB
# This script handles the upgrade process from one version to another

param(
    [string]$TargetVersion = "latest",
    [switch]$SkipBackup = $false
)

Write-Host "开始升级过程..." -ForegroundColor Green
Write-Host "目标版本: $TargetVersion" -ForegroundColor Cyan

# Check if we're in the project directory
if (-not (Test-Path "pyproject.toml")) {
    Write-Host "错误: 请在项目根目录运行此脚本" -ForegroundColor Red
    exit 1
}

# Get current version
$currentVersion = (Select-String -Path "pyproject.toml" -Pattern 'version = "').Line -replace '.*version = "(.*)".*', '$1'
Write-Host "当前版本: $currentVersion" -ForegroundColor Cyan

# Backup current state
if (-not $SkipBackup) {
    Write-Host "创建备份..." -ForegroundColor Yellow
    $backupDir = "backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    New-Item -ItemType Directory -Path $backupDir | Out-Null
    
    # Backup important files
    Copy-Item "pyproject.toml" -Destination $backupDir
    Copy-Item "configs" -Destination $backupDir -Recurse -Force
    if (Test-Path "data") {
        Copy-Item "data" -Destination $backupDir -Recurse -Force
    }
    
    Write-Host "备份完成: $backupDir" -ForegroundColor Green
}

# Check for updates
Write-Host "检查更新..." -ForegroundColor Yellow
try {
    $latestRelease = Invoke-RestMethod -Uri "https://api.github.com/repos/colbertlee/10K_long-doc-RAG-KB/releases/latest"
    $latestVersion = $latestRelease.tag_name -replace 'v', ''
    Write-Host "最新版本: $latestVersion" -ForegroundColor Cyan
    
    if ($currentVersion -eq $latestVersion -and $TargetVersion -eq "latest") {
        Write-Host "已经是最新版本，无需升级" -ForegroundColor Green
        exit 0
    }
    
    $targetVersion = if ($TargetVersion -eq "latest") { $latestVersion } else { $TargetVersion }
    
} catch {
    Write-Host "无法检查更新，继续手动升级" -ForegroundColor Yellow
    $targetVersion = $TargetVersion
}

# Stop services if running
Write-Host "停止运行中的服务..." -ForegroundColor Yellow
try {
    Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*uvicorn*" } | Stop-Process -Force
    Get-Process -Name "ollama" -ErrorAction SilentlyContinue | Stop-Process -Force
    Write-Host "服务已停止" -ForegroundColor Green
} catch {
    Write-Host "没有运行中的服务或停止失败" -ForegroundColor Yellow
}

# Pull latest changes
Write-Host "拉取最新代码..." -ForegroundColor Yellow
try {
    git fetch origin
    git checkout master
    git pull origin master
    Write-Host "代码更新完成" -ForegroundColor Green
} catch {
    Write-Host "Git操作失败，请手动更新代码" -ForegroundColor Red
    exit 1
}

# Checkout specific version if needed
if ($targetVersion -ne "latest" -and $targetVersion -ne $currentVersion) {
    Write-Host "切换到版本 $targetVersion..." -ForegroundColor Yellow
    try {
        git checkout "v$targetVersion"
        Write-Host "版本切换完成" -ForegroundColor Green
    } catch {
        Write-Host "版本切换失败" -ForegroundColor Red
        exit 1
    }
}

# Update dependencies
Write-Host "更新依赖..." -ForegroundColor Yellow
try {
    python -m pip install --upgrade pip
    pip install -e .
    Write-Host "依赖更新完成" -ForegroundColor Green
} catch {
    Write-Host "依赖更新失败" -ForegroundColor Red
    exit 1
}

# Run database migrations if needed
Write-Host "检查数据库迁移..." -ForegroundColor Yellow
# Add migration logic here if needed in future versions
Write-Host "无需数据库迁移" -ForegroundColor Green

# Verify installation
Write-Host "验证安装..." -ForegroundColor Yellow
try {
    python -c "import rag_kb; print('RAG KB导入成功')"
    Write-Host "安装验证成功" -ForegroundColor Green
} catch {
    Write-Host "安装验证失败" -ForegroundColor Red
    exit 1
}

# Restart services
Write-Host "重启服务..." -ForegroundColor Yellow
Write-Host "请手动运行 .\scripts\start.ps1 启动服务" -ForegroundColor Cyan

Write-Host "升级完成！" -ForegroundColor Green
Write-Host "新版本: $targetVersion" -ForegroundColor Cyan
Write-Host "备份位置: $backupDir" -ForegroundColor Cyan