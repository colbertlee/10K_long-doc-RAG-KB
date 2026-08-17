# GitHub Release Automation Script
# This script helps push the repository to GitHub and create a release

# Configuration
$GITHUB_USERNAME = "YOUR_USERNAME"  # Replace with your GitHub username
$REPO_NAME = "10K_long-doc-RAG-KB"  # Replace with your repository name
$VERSION = "v0.1.0"

Write-Host "=== GitHub Release Automation ===" -ForegroundColor Green
Write-Host "Repository: $GITHUB_USERNAME/$REPO_NAME" -ForegroundColor Cyan
Write-Host "Version: $VERSION" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check if git remote is configured
Write-Host "Step 1: Checking git remote configuration..." -ForegroundColor Yellow
$remotes = git remote
if ($remotes -match "origin") {
    Write-Host "Git remote 'origin' is configured" -ForegroundColor Green
} else {
    Write-Host "Git remote 'origin' is not configured" -ForegroundColor Red
    $remote_url = Read-Host "Enter your GitHub repository URL (https://github.com/$GITHUB_USERNAME/$REPO_NAME.git)"
    git remote add origin $remote_url
    Write-Host "Git remote 'origin' added" -ForegroundColor Green
}
Write-Host ""

# Step 2: Push to GitHub
Write-Host "Step 2: Pushing to GitHub..." -ForegroundColor Yellow
try {
    git push -u origin master
    Write-Host "Code pushed to GitHub successfully" -ForegroundColor Green
} catch {
    Write-Host "Failed to push to GitHub: $_" -ForegroundColor Red
    Write-Host "Please check your GitHub credentials and try again" -ForegroundColor Yellow
    exit 1
}
Write-Host ""

# Step 3: Push tags
Write-Host "Step 3: Pushing tags to GitHub..." -ForegroundColor Yellow
try {
    git push origin $VERSION
    Write-Host "Tags pushed to GitHub successfully" -ForegroundColor Green
} catch {
    Write-Host "Failed to push tags: $_" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 4: Create GitHub Release using GitHub CLI
Write-Host "Step 4: Creating GitHub Release..." -ForegroundColor Yellow

# Check if GitHub CLI is installed
$gh_installed = Get-Command gh -ErrorAction SilentlyContinue
if ($gh_installed) {
    Write-Host "GitHub CLI found, creating release automatically..." -ForegroundColor Green
    
    # Read release notes
    $release_notes_path = "docs\RELEASE_NOTES.md"
    if (Test-Path $release_notes_path)) {
        $release_notes = Get-Content $release_notes_path -Raw
    } else {
        $release_notes = "Release $VERSION"
    }
    
    try {
        gh release create $VERSION `
            --title "Version $VERSION" `
            --notes "$release_notes" `
            --repo "$GITHUB_USERNAME/$REPO_NAME"
        Write-Host "GitHub release created successfully" -ForegroundColor Green
    } catch {
        Write-Host "Failed to create GitHub release: $_" -ForegroundColor Red
        Write-Host "Please create the release manually at: https://github.com/$GITHUB_USERNAME/$REPO_NAME/releases/new" -ForegroundColor Yellow
    }
} else {
    Write-Host "GitHub CLI not found" -ForegroundColor Yellow
    Write-Host "Please install GitHub CLI from: https://cli.github.com/" -ForegroundColor Cyan
    Write-Host "Or create the release manually at: https://github.com/$GITHUB_USERNAME/$REPO_NAME/releases/new" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== Release Process Complete ===" -ForegroundColor Green
Write-Host "Repository URL: https://github.com/$GITHUB_USERNAME/$REPO_NAME" -ForegroundColor Cyan
Write-Host "Release URL: https://github.com/$GITHUB_USERNAME/$REPO_NAME/releases/tag/$VERSION" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Visit the repository on GitHub" -ForegroundColor White
Write-Host "2. Verify the release was created successfully" -ForegroundColor White
Write-Host "3. Test the installation from GitHub" -ForegroundColor White
Write-Host "4. Share the release with users" -ForegroundColor White