# 完全自动化GitHub发布脚本
# 此脚本将自动完成从创建仓库到发布Release的全部流程

param(
    [string]$GitHubUsername = "colbertlee",
    [string]$RepoName = "10K_long-doc-RAG-KB",
    [string]$Version = "v0.1.0",
    [switch]$SkipRepoCreation = $false
)

Write-Host "=== RAG知识库完全自动化GitHub发布 ===" -ForegroundColor Green
Write-Host ""

# 配置
$RepoUrl = "https://github.com/$GitHubUsername/$RepoName.git"
$RepoWebUrl = "https://github.com/$GitHubUsername/$RepoName"
$ReleaseNotesPath = "docs\RELEASE_NOTES_CN.md"

Write-Host "发布配置:" -ForegroundColor Cyan
Write-Host "  GitHub用户: $GitHubUsername" -ForegroundColor White
Write-Host "  仓库名称: $RepoName" -ForegroundColor White
Write-Host "  版本: $Version" -ForegroundColor White
Write-Host "  仓库URL: $RepoUrl" -ForegroundColor White
Write-Host ""

# 切换到项目目录
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Split-Path -Parent $ScriptDir
Set-Location $ProjectDir

# Step 1: 检查GitHub CLI
Write-Host "Step 1: 检查GitHub CLI" -ForegroundColor Yellow
$gh_installed = Get-Command gh -ErrorAction SilentlyContinue
if (-not $gh_installed) {
    Write-Host "GitHub CLI未安装，请先安装: https://cli.github.com/" -ForegroundColor Red
    exit 1
}
Write-Host "GitHub CLI已安装" -ForegroundColor Green
Write-Host ""

# Step 2: 检查GitHub认证
Write-Host "Step 2: 检查GitHub认证" -ForegroundColor Yellow
try {
    $auth_status = gh auth status
    Write-Host "GitHub认证状态: 已认证" -ForegroundColor Green
} catch {
    Write-Host "GitHub未认证，正在认证..." -ForegroundColor Yellow
    gh auth login
    Write-Host "GitHub认证完成" -ForegroundColor Green
}
Write-Host ""

# Step 3: 创建GitHub仓库
if (-not $SkipRepoCreation) {
    Write-Host "Step 3: 创建GitHub仓库" -ForegroundColor Yellow
    try {
        # 检查仓库是否已存在
        $repo_exists = gh repo view $GitHubUsername/$RepoName --json name -q .name 2>$null
        if ($repo_exists) {
            Write-Host "仓库已存在: $RepoWebUrl" -ForegroundColor Green
        } else {
            Write-Host "创建新仓库..." -ForegroundColor Cyan
            gh repo create $GitHubUsername/$RepoName `
                --public `
                --description "Enterprise-grade RAG Knowledge Base for 10K+ long documents with LightRAG graph-enhanced retrieval" `
                --source=. `
                --remote=origin `
                --push
            Write-Host "仓库创建成功: $RepoWebUrl" -ForegroundColor Green
        }
    } catch {
        Write-Host "仓库创建失败: $_" -ForegroundColor Red
        Write-Host "请手动创建仓库: https://github.com/new" -ForegroundColor Yellow
        exit 1
    }
} else {
    Write-Host "跳过仓库创建步骤" -ForegroundColor Yellow
}
Write-Host ""

# Step 4: 配置Git远程仓库
Write-Host "Step 4: 配置Git远程仓库" -ForegroundColor Yellow
try {
    $remotes = git remote
    if ($remotes -match "origin") {
        Write-Host "Git远程仓库'origin'已配置" -ForegroundColor Green
        git remote set-url origin $RepoUrl
    } else {
        Write-Host "添加Git远程仓库..." -ForegroundColor Cyan
        git remote add origin $RepoUrl
        Write-Host "Git远程仓库添加成功" -ForegroundColor Green
    }
} catch {
    Write-Host "Git远程仓库配置失败: $_" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 5: 推送代码到GitHub
Write-Host "Step 5: 推送代码到GitHub" -ForegroundColor Yellow
try {
    Write-Host "推送master分支..." -ForegroundColor Cyan
    git push -u origin master --force
    Write-Host "代码推送成功" -ForegroundColor Green
} catch {
    Write-Host "代码推送失败: $_" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 6: 推送标签
Write-Host "Step 6: 推送标签到GitHub" -ForegroundColor Yellow
try {
    # 检查标签是否存在
    $tag_exists = git tag -l "$Version"
    if (-not $tag_exists) {
        Write-Host "创建标签 $Version..." -ForegroundColor Cyan
        git tag -a $Version -m "Release $Version"
    }
    
    Write-Host "推送标签..." -ForegroundColor Cyan
    git push origin $Version --force
    Write-Host "标签推送成功" -ForegroundColor Green
} catch {
    Write-Host "标签推送失败: $_" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 7: 创建GitHub Release
Write-Host "Step 7: 创建GitHub Release" -ForegroundColor Yellow
try {
    # 读取发布说明
    if (Test-Path $ReleaseNotesPath)) {
        $releaseNotes = Get-Content $ReleaseNotesPath -Raw
    } else {
        $releaseNotes = "Release $Version - RAG知识库版本发布"
    }
    
    # 检查Release是否已存在
    $release_exists = gh release view $Version --repo $GitHubUsername/$RepoName --json name -q .name 2>$null
    if ($release_exists) {
        Write-Host "Release $Version 已存在，删除旧Release..." -ForegroundColor Yellow
        gh release delete $Version --repo $GitHubUsername/$RepoName --yes
    }
    
    Write-Host "创建Release..." -ForegroundColor Cyan
    gh release create $Version `
        --title "Release $Version" `
        --notes "$releaseNotes" `
        --repo $GitHubUsername/$RepoName
    Write-Host "GitHub Release创建成功" -ForegroundColor Green
} catch {
    Write-Host "GitHub Release创建失败: $_" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 8: 验证发布
Write-Host "Step 8: 验证发布" -ForegroundColor Yellow
Write-Host "验证以下内容:" -ForegroundColor White
Write-Host "1. GitHub仓库: $RepoWebUrl" -ForegroundColor Cyan
Write-Host "2. Release: $RepoWebUrl/releases/tag/$Version" -ForegroundColor Cyan
Write-Host "3. 测试安装: pip install git+$RepoUrl.git" -ForegroundColor Cyan
Write-Host ""

# Step 9: 显示完成信息
Write-Host "=== 自动化发布完成 ===" -ForegroundColor Green
Write-Host ""
Write-Host "发布信息:" -ForegroundColor Cyan
Write-Host "  仓库: $RepoWebUrl" -ForegroundColor White
Write-Host "  Release: $RepoWebUrl/releases/tag/$Version" -ForegroundColor White
Write-Host "  版本: $Version" -ForegroundColor White
Write-Host ""
Write-Host "后续步骤:" -ForegroundColor Yellow
Write-Host "1. 访问GitHub仓库验证发布" -ForegroundColor White
Write-Host "2. 测试从GitHub安装" -ForegroundColor White
Write-Host "3. 与用户分享仓库链接" -ForegroundColor White
Write-Host ""
Write-Host "未来版本发布:" -ForegroundColor Yellow
Write-Host "1. 更新pyproject.toml中的版本号" -ForegroundColor White
Write-Host "2. 更新docs/RELEASE_NOTES_CN.md" -ForegroundColor White
Write-Host "3. 运行: .\scripts\auto_release.ps1 -Version v0.2.0" -ForegroundColor White
Write-Host ""
Write-Host "🎉 发布成功！" -ForegroundColor Green