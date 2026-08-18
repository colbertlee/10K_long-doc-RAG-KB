# Smart Release Script - RAG Knowledge Base
# This script automates the complete release process based on the established workflow

param(
    [string]$VersionType = "patch",  # major, minor, or patch
    [string]$ReleaseTitle = "",
    [string]$ReleaseNotes = "",
    [switch]$SkipPush = $false,
    [switch]$SkipRelease = $false,
    [switch]$DryRun = $false
)

# Configuration
$GITHUB_USERNAME = "colbertlee"
$REPO_NAME = "10K_long-doc-RAG-KB"
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$PROJECT_DIR = Split-Path -Parent $SCRIPT_DIR

Write-Host "=== RAG Knowledge Base Smart Release ===" -ForegroundColor Green
Write-Host ""

# Function to increment version
function Increment-Version {
    param(
        [string]$CurrentVersion,
        [string]$Type
    )
    
    $parts = $CurrentVersion -split '\.'
    $major = [int]$parts[0]
    $minor = [int]$parts[1]
    $patch = [int]$parts[2]
    
    switch ($Type) {
        "major" {
            $major++
            $minor = 0
            $patch = 0
        }
        "minor" {
            $minor++
            $patch = 0
        }
        "patch" {
            $patch++
        }
        default {
            $patch++
        }
    }
    
    return "$major.$minor.$patch"
}

# Step 1: Read current version
Write-Host "Step 1: Reading current version" -ForegroundColor Yellow
$pyprojectPath = Join-Path $PROJECT_DIR "pyproject.toml"
if (Test-Path $pyprojectPath) {
    $content = Get-Content $pyprojectPath -Raw
    if ($content -match 'version\s*=\s*["'']([^"'']+)["'']') {
        $currentVersion = $Matches[1]
        Write-Host "Current version: $currentVersion" -ForegroundColor Cyan
    } else {
        Write-Host "Cannot read version from pyproject.toml" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "pyproject.toml not found" -ForegroundColor Red
    exit 1
}

# Step 2: Calculate new version
Write-Host "Step 2: Calculating new version" -ForegroundColor Yellow
$newVersion = Increment-Version -CurrentVersion $currentVersion -Type $VersionType
$versionTag = "v$newVersion"
Write-Host "New version: $newVersion" -ForegroundColor Cyan
Write-Host "Version tag: $versionTag" -ForegroundColor Cyan
Write-Host ""

# Display configuration
Write-Host "Release Configuration:" -ForegroundColor Cyan
Write-Host "  Current Version: $currentVersion" -ForegroundColor White
Write-Host "  New Version: $newVersion" -ForegroundColor White
Write-Host "  Version Tag: $versionTag" -ForegroundColor White
Write-Host "  Version Type: $VersionType" -ForegroundColor White
Write-Host "  Repository: $GITHUB_USERNAME/$REPO_NAME" -ForegroundColor White
Write-Host "  Skip Push: $SkipPush" -ForegroundColor White
Write-Host "  Skip Release: $SkipRelease" -ForegroundColor White
Write-Host "  Dry Run: $DryRun" -ForegroundColor White
Write-Host ""

# Confirm release
if (-not $DryRun) {
    $response = Read-Host "Continue with release? (Y/n)"
    if ($response -eq 'n' -or $response -eq 'N') {
        Write-Host "Release cancelled" -ForegroundColor Yellow
        exit 0
    }
} else {
    Write-Host "DRY RUN MODE - No changes will be made" -ForegroundColor Yellow
    Write-Host ""
}

# Change to project directory
Set-Location $PROJECT_DIR

# Step 3: Update version in pyproject.toml
Write-Host "Step 3: Updating version in pyproject.toml" -ForegroundColor Yellow
if (-not $DryRun) {
    $pattern = "version\s*=\s*[""']$currentVersion[""']"
    $replacement = "version = ""$newVersion"""
    $newContent = $content -replace $pattern, $replacement
    Set-Content $pyprojectPath $newContent -Encoding UTF8
    Write-Host "Version updated to $newVersion" -ForegroundColor Green
} else {
    Write-Host "[DRY RUN] Would update version to $newVersion" -ForegroundColor Cyan
}
Write-Host ""

# Step 4: Update release notes
Write-Host "Step 4: Updating release notes" -ForegroundColor Yellow
$releaseNotesPath = Join-Path $PROJECT_DIR "docs\RELEASE_NOTES.md"
$releaseNotesPathCN = Join-Path $PROJECT_DIR "docs\RELEASE_NOTES_CN.md"

if (-not $DryRun) {
    # Update English release notes
    if (Test-Path $releaseNotesPath) {
        $notesContent = Get-Content $releaseNotesPath -Raw
        $currentDate = Get-Date -Format "yyyy-MM-dd"
        $newSection = @"

## [$newVersion] - $currentDate

### Release Notes
- Version bump from $currentVersion to $newVersion
- For detailed changes, see commit history

"@
        $pattern = "(# Release Notes)"
        $updatedNotes = $notesContent -replace $pattern, "`$1$newSection"
        Set-Content $releaseNotesPath $updatedNotes -Encoding UTF8
        Write-Host "Updated RELEASE_NOTES.md" -ForegroundColor Green
    }

    # Update Chinese release notes
    if (Test-Path $releaseNotesPathCN) {
        $notesContentCN = Get-Content $releaseNotesPathCN -Raw
        $currentDate = Get-Date -Format "yyyy-MM-dd"
        $newSectionCN = @"

## [$newVersion] - $currentDate

### 发布说明
- 版本从 $currentVersion 升级到 $newVersion
- 详细更改请查看提交历史

"@
        $patternCN = "(# 发布说明)"
        $updatedNotesCN = $notesContentCN -replace $patternCN, "`$1$newSectionCN"
        Set-Content $releaseNotesPathCN $updatedNotesCN -Encoding UTF8
        Write-Host "Updated RELEASE_NOTES_CN.md" -ForegroundColor Green
    }
} else {
    Write-Host "[DRY RUN] Would update release notes" -ForegroundColor Cyan
}
Write-Host ""

# Step 5: Commit changes
Write-Host "Step 5: Committing changes" -ForegroundColor Yellow
if (-not $DryRun) {
    git add pyproject.toml docs/RELEASE_NOTES.md docs/RELEASE_NOTES_CN.md
    $commitMessage = "chore: bump version to $newVersion and update release notes

Bump version from $currentVersion to $newVersion.

Generated with [Devin](https://devin.ai)

Co-Authored-By: Devin <158243242+devin-ai-integration[bot]@users.noreply.github.com>"
    
    git commit -m $commitMessage
    Write-Host "Changes committed" -ForegroundColor Green
} else {
    Write-Host "[DRY RUN] Would commit changes" -ForegroundColor Cyan
}
Write-Host ""

# Step 6: Push to GitHub
if (-not $SkipPush) {
    Write-Host "Step 6: Pushing to GitHub" -ForegroundColor Yellow
    if (-not $DryRun) {
        try {
            git push origin master
            Write-Host "Code pushed to GitHub" -ForegroundColor Green
        } catch {
            Write-Host "Push failed: $_" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "[DRY RUN] Would push to GitHub" -ForegroundColor Cyan
    }
} else {
    Write-Host "Skipping push step" -ForegroundColor Yellow
}
Write-Host ""

# Step 7: Create GitHub Release
if (-not $SkipRelease) {
    Write-Host "Step 7: Creating GitHub Release" -ForegroundColor Yellow
    
    # Check GitHub CLI
    $gh_installed = Get-Command gh -ErrorAction SilentlyContinue
    if ($gh_installed) {
        Write-Host "GitHub CLI available" -ForegroundColor Green
        
        # Generate release title
        if ([string]::IsNullOrEmpty($ReleaseTitle)) {
            $ReleaseTitle = "v$newVersion - Version Release"
        }
        
        # Generate release notes if not provided
        if ([string]::IsNullOrEmpty($ReleaseNotes)) {
            $ReleaseNotes = "## Version $newVersion

This is a release version $newVersion of the RAG Knowledge Base.

### Changes
- Version bump from $currentVersion to $newVersion
- For detailed changes, see the commit history

### Installation
```powershell
git clone https://github.com/$GITHUB_USERNAME/$REPO_NAME.git
cd $REPO_NAME
pip install -e .
```

### Upgrade
```powershell
git pull origin master
pip install -e .
```

Generated with [Devin](https://devin.ai)"
        }
        
        if (-not $DryRun) {
            try {
                gh release create $versionTag `
                    --title "$ReleaseTitle" `
                    --notes "$ReleaseNotes" `
                    --repo "$GITHUB_USERNAME/$REPO_NAME"
                Write-Host "GitHub Release created successfully!" -ForegroundColor Green
            } catch {
                Write-Host "GitHub Release creation failed: $_" -ForegroundColor Red
                Write-Host "Please create release manually:" -ForegroundColor Yellow
                Write-Host "https://github.com/$GITHUB_USERNAME/$REPO_NAME/releases/new" -ForegroundColor Cyan
            }
        } else {
            Write-Host "[DRY RUN] Would create GitHub release" -ForegroundColor Cyan
        }
    } else {
        Write-Host "GitHub CLI not available" -ForegroundColor Yellow
        Write-Host "Please create release manually:" -ForegroundColor Yellow
        Write-Host "https://github.com/$GITHUB_USERNAME/$REPO_NAME/releases/new" -ForegroundColor Cyan
    }
} else {
    Write-Host "Skipping release creation step" -ForegroundColor Yellow
}
Write-Host ""

# Step 8: Verification
Write-Host "Step 8: Verification" -ForegroundColor Yellow
Write-Host "Please verify the following:" -ForegroundColor White
Write-Host "1. GitHub Repository: https://github.com/$GITHUB_USERNAME/$REPO_NAME" -ForegroundColor Cyan
Write-Host "2. Release: https://github.com/$GITHUB_USERNAME/$REPO_NAME/releases/tag/$versionTag" -ForegroundColor Cyan
Write-Host "3. Version in pyproject.toml: $newVersion" -ForegroundColor Cyan
Write-Host ""

# Completion
Write-Host "=== Smart Release Complete ===" -ForegroundColor Green
Write-Host "Version: $newVersion" -ForegroundColor Cyan
Write-Host "Tag: $versionTag" -ForegroundColor Cyan
Write-Host "Repository: https://github.com/$GITHUB_USERNAME/$REPO_NAME" -ForegroundColor Cyan
Write-Host ""

if ($DryRun) {
    Write-Host "This was a DRY RUN - No actual changes were made" -ForegroundColor Yellow
    Write-Host "Run without -DryRun to execute the release" -ForegroundColor Cyan
}