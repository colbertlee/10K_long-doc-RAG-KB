# 本地文件夹导入脚本
# 用于将本地文件夹导入到RAG知识库

param(
    [Parameter(Mandatory=$true)]
    [string]$FolderPath,
    
    [Parameter(Mandatory=$false)]
    [string]$UserId = "default",
    
    [Parameter(Mandatory=$false)]
    [string]$KbName = "default",
    
    [Parameter(Mandatory=$false)]
    [string]$ApiUrl = "http://localhost:8000/api/v1",
    
    [Parameter(Mandatory=$false)]
    [switch]$SimpleMode
)

Write-Host "=== RAG知识库本地文件夹导入 ===" -ForegroundColor Green
Write-Host ""

# 验证文件夹路径
if (-not (Test-Path $FolderPath)) {
    Write-Host "错误: 文件夹不存在: $FolderPath" -ForegroundColor Red
    exit 1
}

$folderInfo = Get-Item $FolderPath
if (-not $folderInfo.PSIsContainer) {
    Write-Host "错误: 路径不是文件夹: $FolderPath" -ForegroundColor Red
    exit 1
}

Write-Host "导入配置:" -ForegroundColor Cyan
Write-Host "  文件夹: $FolderPath" -ForegroundColor White
Write-Host "  用户ID: $UserId" -ForegroundColor White
Write-Host "  知识库: $KbName" -ForegroundColor White
Write-Host "  API地址: $ApiUrl" -ForegroundColor White
Write-Host "  简单模式: $SimpleMode" -ForegroundColor White
Write-Host ""

# 统计文件夹信息
$fileCount = (Get-ChildItem -Path $FolderPath -Recurse -File | Measure-Object).Count
$totalSize = (Get-ChildItem -Path $FolderPath -Recurse -File | Measure-Object -Property Length -Sum).Sum / 1MB

Write-Host "文件夹信息:" -ForegroundColor Cyan
Write-Host "  文件数量: $fileCount" -ForegroundColor White
Write-Host "  总大小: $([math]::Round($totalSize, 2)) MB" -ForegroundColor White
Write-Host ""

# 准备API请求
if ($SimpleMode) {
    $endpoint = "$ApiUrl/import-local-folder"
    $body = @{
        folder_path = $FolderPath
        user_id = $UserId
        kb_name = $KbName
        acl = @{
            read = @($UserId)
            write = @($UserId)
        }
    }
} else {
    $endpoint = "$ApiUrl/users/$UserId/kbs/$KbName/import-folder"
    $body = @{
        folder_path = $FolderPath
        acl = @{
            read = @($UserId)
            write = @($UserId)
        }
    }
}

$jsonBody = $body | ConvertTo-Json -Depth 10

Write-Host "开始导入..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri $endpoint `
        -Method Post `
        -Body $jsonBody `
        -ContentType "application/json" `
        -TimeoutSec 300
    
    Write-Host "导入完成!" -ForegroundColor Green
    Write-Host ""
    Write-Host "导入结果:" -ForegroundColor Cyan
    Write-Host "  成功: $($response.success)" -ForegroundColor White
    Write-Host "  源文件夹: $($response.source_folder)" -ForegroundColor White
    Write-Host "  发现文件总数: $($response.total_files_found)" -ForegroundColor White
    Write-Host "  处理文件数: $($response.files_processed)" -ForegroundColor White
    Write-Host "  跳过文件数: $($response.files_skipped)" -ForegroundColor White
    Write-Host "  失败文件数: $($response.files_failed)" -ForegroundColor White
    
    if ($response.files_processed -gt 0) {
        Write-Host ""
        Write-Host "处理的文档:" -ForegroundColor Cyan
        foreach ($doc in $response.documents) {
            Write-Host "  - $($doc.filename)" -ForegroundColor White
        }
    }
    
    if ($response.files_skipped -gt 0) {
        Write-Host ""
        Write-Host "跳过的文件:" -ForegroundColor Yellow
        foreach ($file in $response.skipped_files) {
            Write-Host "  - $file" -ForegroundColor White
        }
    }
    
    if ($response.files_failed -gt 0) {
        Write-Host ""
        Write-Host "失败的文件:" -ForegroundColor Red
        foreach ($file in $response.failed_files) {
            Write-Host "  - $($file.file): $($file.error)" -ForegroundColor White
        }
    }
    
    Write-Host ""
    Write-Host "知识库信息:" -ForegroundColor Cyan
    Write-Host "  用户ID: $($response.user_id)" -ForegroundColor White
    Write-Host "  知识库名称: $($response.kb_name)" -ForegroundColor White
    
} catch {
    Write-Host "导入失败: $_" -ForegroundColor Red
    if ($_.Exception.Response) {
        $errorResponse = $_.Exception.Response.GetResponseStream()
        $reader = New-Object System.IO.StreamReader($errorResponse)
        $responseBody = $reader.ReadToEnd()
        Write-Host "错误详情: $responseBody" -ForegroundColor Yellow
    }
    exit 1
}

Write-Host ""
Write-Host "导入完成! 您现在可以查询知识库了。" -ForegroundColor Green