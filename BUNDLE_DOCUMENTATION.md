# VitaNet Bundle System

VitaNet now includes a comprehensive bundle system for backing up and restoring your application data and configuration.

## What is a VitaNet Bundle?

A VitaNet bundle is a `.vitanet` file that contains:
- Database backup (SQLite database file)
- Database schema (SQL CREATE statements)
- Database data (SQL INSERT statements)
- Bundle metadata (version, creation date, custom metadata)

## Features

- **Create bundles**: Export your VitaNet data into portable bundle files
- **Restore bundles**: Import data from bundle files
- **Bundle information**: Inspect bundle contents without restoring
- **Multiple interfaces**: REST API, CLI tool, and Python library
- **Safe restoration**: Automatic backup creation before overwriting
- **Version validation**: Ensures bundle compatibility

## REST API Endpoints

### Get Bundle Status
```
GET /api/bundle/status
```
Returns current VitaNet database status and bundle capabilities.

### Create Bundle
```
POST /api/bundle/create
Content-Type: application/json

{
  "filename": "optional_custom_filename",
  "metadata": {
    "description": "Optional description",
    "tags": ["tag1", "tag2"]
  }
}
```
Returns a downloadable `.vitanet` bundle file.

### Restore Bundle
```
POST /api/bundle/restore
Content-Type: multipart/form-data

Form data:
- bundle_file: The .vitanet bundle file
- force: "true" to overwrite existing database (optional)
```
Restores VitaNet from the uploaded bundle.

### Get Bundle Info
```
POST /api/bundle/info
Content-Type: multipart/form-data

Form data:
- bundle_file: The .vitanet bundle file
```
Returns information about the bundle without restoring it.

## CLI Tool Usage

The `vitanet_bundle_cli.py` script provides command-line access to bundle operations:

### Check Status
```bash
python vitanet_bundle_cli.py status
```

### Create Bundle
```bash
python vitanet_bundle_cli.py create backup.vitanet --description "Daily backup"
```

### Restore Bundle
```bash
python vitanet_bundle_cli.py restore backup.vitanet --force
```

### Get Bundle Info
```bash
python vitanet_bundle_cli.py info backup.vitanet
```

## Python Library Usage

```python
from bundle_manager import VitaNetBundleManager

# Initialize
manager = VitaNetBundleManager(db_path="vitanet.db")

# Create bundle
result = manager.create_bundle("backup.vitanet", {"description": "My backup"})
if result['success']:
    print(f"Bundle created: {result['bundle_path']}")

# Restore bundle
result = manager.restore_bundle("backup.vitanet", force=True)
if result['success']:
    print("Bundle restored successfully")

# Get bundle info
result = manager.list_bundle_info("backup.vitanet")
if result['success']:
    print(f"Bundle created: {result['metadata']['created_at']}")
```

## Examples

### API Examples with curl

**Create a bundle:**
```bash
curl -X POST http://localhost:5000/api/bundle/create \
  -H "Content-Type: application/json" \
  -d '{"metadata": {"description": "API backup"}}' \
  --output my_backup.vitanet
```

**Get bundle information:**
```bash
curl -X POST http://localhost:5000/api/bundle/info \
  -F "bundle_file=@my_backup.vitanet"
```

**Restore a bundle:**
```bash
curl -X POST http://localhost:5000/api/bundle/restore \
  -F "bundle_file=@my_backup.vitanet" \
  -F "force=true"
```

### CLI Examples

**Daily backup script:**
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
python vitanet_bundle_cli.py create "backup_$DATE.vitanet" --description "Automated daily backup"
```

**Restore from latest backup:**
```bash
# Find latest backup
LATEST=$(ls -t backup_*.vitanet | head -1)
python vitanet_bundle_cli.py restore "$LATEST" --force
```

## Bundle File Structure

A `.vitanet` bundle is a ZIP file containing:

```
bundle_metadata.json     - Bundle information and metadata
vitanet_backup.db       - Complete database backup (if database exists)
schema.sql              - Database schema (CREATE statements)
data.sql                - Database data (INSERT statements)
```

### Bundle Metadata Format

```json
{
  "version": "1.0",
  "created_at": "2025-07-13T14:05:31.041586+00:00",
  "vitanet_version": "1.0",
  "database_included": true,
  "custom_metadata": {
    "description": "User-provided description",
    "tags": ["backup", "production"]
  }
}
```

## Error Handling

The bundle system includes comprehensive error handling:

- **File not found**: Clear error when bundle file doesn't exist
- **Version mismatch**: Prevents restoring incompatible bundles
- **Database conflicts**: Requires `force=true` to overwrite existing data
- **Corrupted bundles**: Validates bundle structure before restoration
- **Permission issues**: Clear error messages for file system problems

## Security Considerations

- Bundle files contain complete database contents
- Store bundle files securely
- Use appropriate file permissions
- Consider encrypting bundle files for sensitive data
- Validate bundle sources before restoration

## Troubleshooting

**Bundle creation fails:**
- Check database file permissions
- Ensure sufficient disk space
- Verify database is not locked

**Bundle restoration fails:**
- Check if target database exists (use `--force` if needed)
- Verify bundle file integrity
- Ensure compatible bundle version

**API endpoints not working:**
- Verify Flask app is running
- Check that bundle_api blueprint is registered
- Ensure all dependencies are installed

## Integration with Existing Workflows

The bundle system is designed to integrate seamlessly with:
- Automated backup scripts
- CI/CD pipelines
- Data migration workflows
- Development environment setup
- Disaster recovery procedures