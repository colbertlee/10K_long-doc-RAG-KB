# Upgrade Guide - RAG Knowledge Base

## Version 0.1.0 → Future Versions

### Checking Current Version

To check your current installed version:

```bash
pip show rag-kb
```

### Upgrading from GitHub

#### Method 1: Using pip (Recommended)

```bash
# Upgrade to the latest version
pip install --upgrade rag-kb

# Or upgrade to a specific version
pip install rag-kb==0.2.0
```

#### Method 2: From GitHub Repository

```bash
# Clone or pull latest changes
cd 10K_long-doc-RAG-KB
git pull origin master

# Reinstall with latest changes
pip install -e .
```

### Post-Upgrade Steps

#### 1. Backup Current Data

Before upgrading, always backup your data:

```bash
# Backup data directory
Copy-Item -Recurse data data_backup_$(Get-Date -Format 'yyyyMMdd')

# Backup LightRAG database
Copy-Item -Recurse lightrag_db lightrag_db_backup_$(Get-Date -Format 'yyyyMMdd')
```

#### 2. Update Configuration

Check if there are any new configuration options in the latest `config.example.yaml`:

```bash
# Compare your config with the example
Compare-Object (Get-Content configs\config.yaml) (Get-Content configs\config.example.yaml)
```

#### 3. Update Dependencies

```bash
# Update all dependencies
pip install --upgrade -r requirements.txt

# Or update specific optional dependencies
pip install --upgrade -e ".[lightrag,sentence-transformers]"
```

#### 4. Database Migration (if required)

Some versions may require database migrations. Check the release notes for specific migration instructions.

```bash
# If migration is needed, follow the specific instructions
# from the release notes
```

#### 5. Restart Services

```bash
# Stop current services
# (Stop Ollama, FastAPI, Open WebUI)

# Start services with new version
.\scripts\start.ps1
```

### Version-Specific Upgrade Instructions

#### Upgrading to v0.2.0 (Example)

When v0.2.0 is released, follow these steps:

1. **Check Release Notes**: Read `docs/RELEASE_NOTES.md` for v0.2.0 changes
2. **Backup Data**: Backup your `data/` and `lightrag_db/` directories
3. **Update Configuration**: Add any new configuration options
4. **Run Migration**: If database schema changed, run migration scripts
5. **Test**: Verify basic functionality before production use

### Rollback Instructions

If you need to rollback to a previous version:

```bash
# Install specific previous version
pip install rag-kb==0.1.0

# Or from git
git checkout tags/v0.1.0
pip install -e .
```

### Troubleshooting Upgrades

#### Import Errors After Upgrade

If you encounter import errors:

```bash
# Clear Python cache
python -m pip cache purge

# Reinstall the package
pip uninstall rag-kb
pip install -e .
```

#### Configuration Issues

If configuration is incompatible:

```bash
# Backup your current config
copy configs\config.yaml configs\config.yaml.backup

# Copy the new example config
copy configs\config.example.yaml configs\config.yaml

# Manually merge your settings
```

#### Database Compatibility Issues

If LightRAG database is incompatible:

```bash
# Backup current database
Copy-Item -Recurse lightrag_db lightrag_db_backup

# Rebuild index (if needed)
python scripts\ingest_bulk.py
```

### Automatic Upgrade Script

Create an automatic upgrade script:

```powershell
# scripts/upgrade.ps1

Write-Host "Starting upgrade process..." -ForegroundColor Green

# Backup
$backup_date = Get-Date -Format 'yyyyMMdd'
Copy-Item -Recurse data "data_backup_$backup_date"
Copy-Item -Recurse lightrag_db "lightrag_db_backup_$backup_date"
Write-Host "Backup completed: data_backup_$backup_date" -ForegroundColor Cyan

# Update code
git pull origin master
Write-Host "Code updated from GitHub" -ForegroundColor Cyan

# Update dependencies
pip install --upgrade -e .
Write-Host "Dependencies updated" -ForegroundColor Cyan

# Restart services
Write-Host "Please restart services manually using .\scripts\start.ps1" -ForegroundColor Yellow
```

### Monitoring Upgrade Health

After upgrading, monitor the system:

1. **Check Logs**: Review logs for any errors
2. **Test Queries**: Run sample queries to verify functionality
3. **Performance**: Check if performance is degraded
4. **Compatibility**: Verify all features work as expected

### Getting Help

If you encounter issues during upgrade:

1. Check the [Release Notes](RELEASE_NOTES.md) for known issues
2. Review [Troubleshooting](USER_GUIDE.md#troubleshooting) section
3. Open a GitHub Issue with detailed error information
4. Check GitHub Discussions for community help

### Best Practices

1. **Always Backup**: Never upgrade without backing up data
2. **Test First**: Test upgrades in a staging environment
3. **Read Release Notes**: Understand what changed before upgrading
4. **Monitor After Upgrade**: Watch for issues in the first 24 hours
5. **Keep Documentation Updated**: Maintain local upgrade notes

### Upgrade Schedule

Recommended upgrade schedule:

- **Critical Security Updates**: Immediately
- **Feature Updates**: Within 1-2 weeks
- **Bug Fixes**: As needed
- **Major Versions**: Plan and test thoroughly

### Release Channels

- **Stable**: Recommended for production use
- **Beta**: New features, use with caution
- **Development**: Latest features, may be unstable

Choose the appropriate release channel based on your needs.