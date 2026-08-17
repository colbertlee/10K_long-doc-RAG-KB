# 自动发布脚本 - RAG 知识库
# 此脚本自动完成版本发布流程

param(
    [string]$Version = "",
    [switch]$SkipPush = $false,
    [switch]$SkipRelease = $false
)

# 配置
$GITHUB_USERNAME = "colbertlee"
$REPO_NAME = "10K_long-doc-RAG-KB"
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$PROJECT_DIR = Split-Path -Parent $SCRIPT_DIR

Write-Host "=== RAG 知识库自动发布 ===" -ForegroundColor Green
Write-Host ""

# 如果没有指定版本，从 pyproject.toml 读取
if ([string]::IsNullOrEmpty($Version)) {
    $pyproject = Join-Path $PROJECT_DIR "pyproject.toml"
    if (Test-Path $pyproject) {
        $content = Get-Content $pyproject -Raw
        if ($content -match 'version\s*=\s*["'']([^"'']+)["'']') {
            $Version = "v" + $Matches[1]
            Write-Host "从 pyproject.toml 读取版本: $Version" -ForegroundColor Cyan
        } else {
            Write-Host "无法从 pyproject.toml 读取版本" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "pyproject.toml 文件不存在" -ForegroundColor Red
        exit 1
    }
}

Write-Host "发布配置:" -ForegroundColor Cyan
Write-Host "  版本: $Version" -ForegroundColor White
Write-Host "  仓库: $GITHUB_USERNAME/$REPO_NAME" -ForegroundColor White
Write-Host "  跳过推送: $SkipPush" -ForegroundColor White
Write-Host "  跳过 Release: $SkipRelease" -ForegroundColor White
Write-Host ""

# 验证版本格式
if ($Version -notmatch '^v\d+\.\d+\.\d+$') {
    Write-Host "版本格式错误，应为 v0.1.0 格式" -ForegroundColor Red
    exit 1
}

# 切换到项目目录
Set-Location $PROJECT_DIR

# Step 1: 检查是否有未提交的更改
Write-Host "Step 1: 检查 Git 状态" -ForegroundColor Yellow
$gitStatus = git status --porcelain
if ($gitStatus) {
    Write-Host "发现未提交的更改:" -ForegroundColor Red
    Write-Host $gitStatus -ForegroundColor Yellow
    $response = Read-Host "是否继续发布？(y/N)"
    if ($response -ne 'y' -and $response -ne 'Y') {
        Write-Host "发布已取消" -ForegroundColor Yellow
        exit 0
    }
} else {
    Write-Host "工作目录干净" -ForegroundColor Green
}
Write-Host ""

# Step 2: 创建 Git 标签
Write-Host "Step 2: 创建 Git 标签" -ForegroundColor Yellow
$tagExists = git tag -l "$Version"
if ($tagExists) {
    Write-Host "标签 $Version 已存在" -ForegroundColor Yellow
    $response = Read-Host "是否删除并重新创建标签？(y/N)"
    if ($response -eq 'y' -or $response -eq 'Y') {
        git tag -d $Version
        Write-Host "已删除旧标签" -ForegroundColor Green
    } else {
        Write-Host "保留现有标签" -ForegroundColor Yellow
    }
}

if (-not (git tag -l "$Version")) {
    git tag -a $Version -m "Release $Version"
    Write-Host "标签 $Version 创建成功" -ForegroundColor Green
} else {
    Write-Host "标签 $Version 已存在，跳过创建" -ForegroundColor Cyan
}
Write-Host ""

# Step 3: 推送到 GitHub
if (-not $SkipPush) {
    Write-Host "Step 3: 推送到 GitHub" -ForegroundColor Yellow
    try {
        # 推送代码
        Write-Host "推送代码..." -ForegroundColor Cyan
        git push origin master
        
        # 推送标签
        Write-Host "推送标签..." -ForegroundColor Cyan
        git push origin $Version
        
        Write-Host "代码和标签推送成功" -ForegroundColor Green
    } catch {
        Write-Host "推送失败: $_" -ForegroundColor Red
        Write-Host "请检查:" -ForegroundColor Yellow
        Write-Host "1. GitHub 仓库已创建" -ForegroundColor White
        Write-Host "2. GitHub 凭证已配置" -ForegroundColor White
        Write-Host "3. 网络连接正常" -ForegroundColor White
        exit 1
    }
} else {
    Write-Host "跳过推送步骤" -ForegroundColor Yellow
}
Write-Host ""

# Step 4: 创建 GitHub Release
if (-not $SkipRelease) {
    Write-Host "Step 4: 创建 GitHub Release" -ForegroundColor Yellow
    
    # 检查 GitHub CLI
    $gh_installed = Get-Command gh -ErrorAction SilentlyContinue
    if ($gh_installed) {
        Write-Host "GitHub CLI 可用，自动创建 Release..." -ForegroundColor Green
        
        # 读取发布说明
        $releaseNotesPath = "docs\RELEASE_NOTES_CN.md"
        if (Test-Path $releaseNotesPath)) {
            $releaseNotes = Get-Content $releaseNotesPath -Raw
        } else {
            $releaseNotes = "Release $Version - RAG 知识库版本发布"
        }
        
        try {
            gh release create $Version `
                --title "Release $Version" `
                --notes "$releaseNotes" `
                --repo "$GITHUB_USERNAME/$REPO_NAME"
            Write-Host "GitHub Release 创建成功！" -ForegroundColor Green
        } catch {
            Write-Host "GitHub Release 创建失败: $_" -ForegroundColor Red
            Write-Host "请手动创建 Release" -ForegroundColor Yellow
            Write-Host "https://github.com/$GITHUB_USERNAME/$REPO_NAME/releases/new" -ForegroundColor Cyan
        }
    } else {
        Write-Host "GitHub CLI 不可用" -ForegroundColor Yellow
        Write-Host "请手动创建 Release:" -ForegroundColor Yellow
        Write-Host "https://github.com/$GITHUB_USERNAME/$REPO_NAME/releases/new" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "手动步骤:" -ForegroundColor White
        Write-Host "1. 访问上述 URL" -ForegroundColor White
        Write-Host "2. 选择标签: $Version" -ForegroundColor White
        Write-Host "3. 标题: Release $Version" -ForegroundColor White
        Write-Host "4. 描述: 复制 docs\RELEASE_NOTES_CN.md 内容" -ForegroundColor White
        Write-Host "5. 点击 'Publish release'" -ForegroundColor White
    }
} else {
    Write-Host "跳过 Release 创建步骤" -ForegroundColor Yellow
}
Write-Host ""

# Step 5: 验证发布
Write-Host "Step 5: 验证发布" -ForegroundColor Yellow
Write-Host "请验证以下内容:" -ForegroundColor White
Write-Host "1. GitHub 仓库: https://github.com/$GITHUB_USERNAME/$REPO_NAME" -ForegroundColor Cyan
Write-Host "2. Release: https://github.com/$GITHUB_USERNAME/$REPO_NAME/releases/tag/$VERSION" -ForegroundColor Cyan
Write-Host "3. 测试安装: pip install git+https://github.com/$GITHUB_USERNAME/$REPO_NAME.git" -ForegroundColor Cyan
Write-Host ""

Write-Host "=== 自动发布完成 ===" -ForegroundColor Green
Write-Host "版本: $Version" -ForegroundColor Cyan
Write-Host "仓库: https://github.com/$GITHUB_USERNAME/$REPO_NAME" -ForegroundColor Cyan
Write-Host ""