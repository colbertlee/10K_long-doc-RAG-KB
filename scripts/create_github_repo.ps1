# GitHub Repository Creation and Release Script
# This script helps create the GitHub repository and perform the initial release

Write-Host "=== GitHub Repository Creation and Release ===" -ForegroundColor Green
Write-Host ""

# Configuration
$GITHUB_USERNAME = "colbertlee"
$REPO_NAME = "10K_long-doc-RAG-KB"
$VERSION = "v0.1.0"
$REPO_URL = "https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"

Write-Host "Configuration:" -ForegroundColor Cyan
Write-Host "  Username: $GITHUB_USERNAME" -ForegroundColor White
Write-Host "  Repository: $REPO_NAME" -ForegroundColor White
Write-Host "  Version: $VERSION" -ForegroundColor White
Write-Host "  URL: $REPO_URL" -ForegroundColor White
Write-Host ""

# Step 1: Instructions for creating repository
Write-Host "Step 1: Create GitHub Repository" -ForegroundColor Yellow
Write-Host "=====================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "Please follow these steps to create the repository:" -ForegroundColor White
Write-Host "1. Open this URL in your browser:" -ForegroundColor Cyan
Write-Host "   https://github.com/new" -ForegroundColor White
Write-Host ""
Write-Host "2. Fill in the repository details:" -ForegroundColor White
Write-Host "   Repository name: $REPO_NAME" -ForegroundColor Yellow
Write-Host "   Description: Enterprise-grade RAG Knowledge Base for 10K+ long documents with LightRAG graph-enhanced retrieval" -ForegroundColor Yellow
Write-Host "   Visibility: Public (recommended)" -ForegroundColor Yellow
Write-Host "   IMPORTANT: Do NOT initialize with README, .gitignore, or license" -ForegroundColor Red
Write-Host ""
Write-Host "3. Click 'Create repository'" -ForegroundColor White
Write-Host ""
Write-Host "Press Enter when you have created the repository..." -ForegroundColor Green
$null = Read-Host
Write-Host ""

# Step 2: Push to GitHub
Write-Host "Step 2: Pushing code to GitHub" -ForegroundColor Yellow
Write-Host "===============================" -ForegroundColor Yellow
Write-Host ""

try {
    # Add remote if not exists
    $remote_exists = git remote | Select-String "origin"
    if (-not $remote_exists) {
        Write-Host "Adding git remote..." -ForegroundColor Cyan
        git remote add origin $REPO_URL
    } else {
        Write-Host "Git remote 'origin' already exists" -ForegroundColor Green
    }
    
    # Push to GitHub
    Write-Host "Pushing to GitHub..." -ForegroundColor Cyan
    git push -u origin master
    Write-Host "Code pushed successfully!" -ForegroundColor Green
    Write-Host ""
    
    # Push tags
    Write-Host "Pushing tags to GitHub..." -ForegroundColor Cyan
    git push origin $VERSION
    Write-Host "Tags pushed successfully!" -ForegroundColor Green
    Write-Host ""
    
} catch {
    Write-Host "Failed to push to GitHub: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please check:" -ForegroundColor Yellow
    Write-Host "1. That you created the repository on GitHub" -ForegroundColor White
    Write-Host "2. That you have proper GitHub credentials configured" -ForegroundColor White
    Write-Host "3. That the repository URL is correct: $REPO_URL" -ForegroundColor White
    exit 1
}

# Step 3: Create GitHub Release
Write-Host "Step 3: Creating GitHub Release" -ForegroundColor Yellow
Write-Host "=============================" -ForegroundColor Yellow
Write-Host ""

# Check if GitHub CLI is available
$gh_installed = Get-Command gh -ErrorAction SilentlyContinue
if ($gh_installed) {
    Write-Host "GitHub CLI found, creating release automatically..." -ForegroundColor Green
    
    # Read release notes
    $release_notes_path = "docs\RELEASE_NOTES.md"
    if (Test-Path $release_notes_path)) {
        $release_notes = Get-Content $release_notes_path -Raw
    } else {
        $release_notes = "Release $VERSION - Initial release of RAG Knowledge Base for 10K long documents"
    }
    
    try {
        gh release create $VERSION `
            --title "Version 0.1.0 - Initial Release" `
            --notes "$release_notes" `
            --repo "$GITHUB_USERNAME/$REPO_NAME"
        Write-Host "GitHub release created successfully!" -ForegroundColor Green
    } catch {
        Write-Host "Failed to create GitHub release: $_" -ForegroundColor Red
        Write-Host "Please create the release manually at:" -ForegroundColor Yellow
        Write-Host "https://github.com/$GITHUB_USERNAME/$REPO_NAME/releases/new" -ForegroundColor Cyan
    }
} else {
    Write-Host "GitHub CLI not found" -ForegroundColor Yellow
    Write-Host "Please create the release manually at:" -ForegroundColor Yellow
    Write-Host "https://github.com/$GITHUB_USERNAME/$REPO_NAME/releases/new" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Manual release steps:" -ForegroundColor White
    Write-Host "1. Go to the URL above" -ForegroundColor White
    Write-Host "2. Select tag: $VERSION" -ForegroundColor White
    Write-Host "3. Title: Version 0.1.0 - Initial Release" -ForegroundColor White
    Write-Host "4. Description: Copy content from docs\RELEASE_NOTES.md" -ForegroundColor White
    Write-Host "5. Click 'Publish release'" -ForegroundColor White
}

Write-Host ""
Write-Host "=== Release Process Complete ===" -ForegroundColor Green
Write-Host ""
Write-Host "Repository: $REPO_URL" -ForegroundColor Cyan
Write-Host "Release: https://github.com/$GITHUB_USERNAME/$REPO_NAME/releases/tag/$VERSION" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Verify the repository on GitHub" -ForegroundColor White
Write-Host "2. Verify the release was created" -ForegroundColor White
Write-Host "3. Test installation: pip install git+$REPO_URL" -ForegroundColor White
Write-Host "4. Share the repository with users" -ForegroundColor White
Write-Host ""
Write-Host "For future releases, use: .\scripts\github_release.ps1" -ForegroundColor Cyan