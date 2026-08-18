# Upgrade Guide - RAG Knowledge Base

## Version 0.1.0 → Future Versions

### Checking Current Version

To check your current installed version:

```bash
# Check version in local pyproject.toml
Select-String -Path "pyproject.toml" -Pattern 'version = "'
```

### Upgrading from GitHub

This project is not published to PyPI, so upgrades must be done through the GitHub repository.

#### Method 1: Using Automatic Upgrade Script (Recommended)

```powershell
# Upgrade to latest version
.\scripts\upgrade.ps1

# Upgrade to specific version
.\scripts\upgrade.ps1 -TargetVersion "0.2.6"

# Skip backup (not recommended)
.\scripts\upgrade.ps1 -SkipBackup
```

The upgrade script will automatically:
1. Check current version and latest version
2. Create data backup
3. Stop running services
4. Pull latest code
5. Update dependencies
6. Verify installation
7. Provide guidance for restarting services

#### Method 2: Manual Upgrade

```bash
# 1. Backup current data
Copy-Item -Recurse data data_backup_$(Get-Date -Format 'yyyyMMdd')
Copy-Item -Recurse lightrag_db lightrag_db_backup_$(Get-Date -Format 'yyyyMMdd')

# 2. Pull latest code
cd 10K_long-doc-RAG-KB
git fetch origin
git checkout master
git pull origin master

# 3. Reinstall with latest changes
pip install -e .

# 4. Update dependencies
pip install --upgrade -r requirements.txt

# 5. Restart services
.\scripts\start.ps1
```

#### Method 3: Upgrade to Specific Version

```bash
# 1. Backup data
Copy-Item -Recurse data data_backup_$(Get-Date -Format 'yyyyMMdd')

# 2. Checkout specific version tag
git fetch --tags
git checkout v0.2.6

# 3. Reinstall
pip install -e .

# 4. Restart services
.\scripts\start.ps1
```

### Post-Upgrade Steps

#### 1. Check Configuration Updates

Check if there are any new configuration options in the latest `config.example.yaml`:

```bash
# Compare your config with the example
Compare-Object (Get-Content configs\config.yaml) (Get-Content configs\config.example.yaml)
```

#### 2. Update Dependencies

```bash
# Update all dependencies
pip install --upgrade -r requirements.txt

# Or update specific optional dependencies
pip install --upgrade -e ".[lightrag,sentence-transformers]"
```

#### 3. Database Migration (if required)

Some versions may require database migrations. Check the release notes for specific migration instructions.

```bash
# If migration is needed, follow the specific instructions
# from the release notes
```

#### 4. Restart Services

```bash
# Stop current services
# (Stop Ollama, FastAPI, Open WebUI)

# Start services with new version
.\scripts\start.ps1
```

### Version-Specific Upgrade Instructions

#### Upgrading to v0.2.6

Key changes in v0.2.6:
- Updated Open WebUI integration to use Python 3.12
- Simplified integration to use separate interfaces
- Removed complex iframe integration

Upgrade steps:
1. **Check Release Notes**: Read `docs/RELEASE_NOTES.md` for v0.2.6 changes
2. **Backup Data**: Backup your `data/` and `lightrag_db/` directories
3. **Update Configuration**: Check for new configuration options
4. **Run Upgrade**: `.\scripts\upgrade.ps1 -TargetVersion "0.2.6"`
5. **Test**: Verify document management UI and Open WebUI functionality

### Rollback Instructions

If you need to rollback to a previous version:

```bash
# 1. Stop services
# Stop all running services

# 2. Checkout specific version tag
git checkout v0.2.5

# 3. Reinstall
pip install -e .

# 4. Restore backup (if needed)
Copy-Item -Recurse data_backup_YYYYMMDD data

# 5. Restart services
.\scripts\start.ps1
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

#### Git Operation Failures

If git pull fails:

```bash
# Check current status
git status

# If there are uncommitted changes, commit or stash them
git stash

# Then pull again
git pull origin master
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

### Important Notes

⚠️ **This project is not published to PyPI**

- Do NOT use `pip install --upgrade rag-kb` command
- Do NOT use `pip install rag-kb==<version>` command
- Upgrades must be done through GitHub repository only
- Use `git pull` or `upgrade.ps1` script for upgrades