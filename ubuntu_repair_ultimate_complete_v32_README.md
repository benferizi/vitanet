# Ubuntu Repair Ultimate Complete Script v32

A comprehensive system repair and maintenance tool for Ubuntu systems with full implementation and no placeholders.

## Features

This script provides complete implementations for:

- **System Diagnostics**: Comprehensive analysis of system health including disk space, system load, and critical services
- **Package Management**: Fix broken packages, resolve dependencies, update package lists
- **Lock File Management**: Detect and remove stale dpkg/apt locks
- **Filesystem Checks**: Verify filesystem status and detect read-only mounts
- **Network Configuration**: Restart NetworkManager and flush DNS cache
- **Boot Loader Repair**: Update and repair GRUB configuration
- **Service Management**: Detect and restart failed systemd units (all types)
- **Log Cleanup**: Rotate and vacuum system logs to free up space
- **System Optimization**: Update locate/man databases and sync filesystems
- **Comprehensive Reporting**: Detailed logs and reports of all operations

## Requirements

- Ubuntu Linux system (tested on 20.04, 22.04, 24.04)
- Python 3.6 or higher
- Root/sudo privileges (except for dry-run mode)

## Installation

No installation required. Simply download the script and make it executable:

```bash
chmod +x ubuntu_repair_ultimate_complete_v32.py
```

## Usage

### Basic Usage (requires sudo)

```bash
sudo python3 ubuntu_repair_ultimate_complete_v32.py
```

### Dry Run Mode (preview without making changes)

```bash
python3 ubuntu_repair_ultimate_complete_v32.py --dry-run
```

### Verbose Output

```bash
sudo python3 ubuntu_repair_ultimate_complete_v32.py --verbose
```

### Combine Options

```bash
python3 ubuntu_repair_ultimate_complete_v32.py --dry-run --verbose
```

## Command Line Options

- `--dry-run`: Perform a dry run without making any actual changes. Useful for testing and preview.
- `--verbose` or `-v`: Enable verbose output showing detailed execution information.
- `--help` or `-h`: Display help message with usage information.

## What It Does

### 1. System Analysis
- Checks disk space usage and warns if > 90% full
- Monitors system load average
- Verifies critical services (ssh, cron, rsyslog, systemd-journald)
- Detects broken or partially installed packages
- Validates APT sources configuration
- Scans system logs for recent errors

### 2. Package Repairs
- Removes stale dpkg/apt lock files
- Configures pending packages (`dpkg --configure -a`)
- Fixes broken dependencies (`apt-get install -f`)
- Updates package lists (`apt-get update`)
- Upgrades packages (`apt-get upgrade`)
- Cleans package cache (`apt-get clean`, `autoclean`, `autoremove`)

### 3. System Maintenance
- Checks filesystem status and detects read-only mounts
- Restarts NetworkManager service
- Flushes DNS cache
- Updates GRUB bootloader configuration
- Restarts failed systemd units (all types: .service, .socket, .timer, .mount, etc.)
- Rotates and vacuums system logs

### 4. Optimization
- Updates locate database
- Updates man database
- Syncs filesystem to ensure data integrity

## Output Files

The script generates several output files in `/tmp/`:

- `ubuntu_repair_YYYYMMDD_HHMMSS.log`: Detailed log of all operations
- `ubuntu_repair_report_YYYYMMDD_HHMMSS.txt`: Summary report of issues found and fixed
- `ubuntu_repair_backup_YYYYMMDD_HHMMSS/`: Directory for backup files (when applicable)

## Safety Features

- **Dry Run Mode**: Test the script without making changes
- **Comprehensive Logging**: All operations are logged for audit purposes
- **Backup Creation**: Critical files are backed up before modification
- **Error Handling**: Graceful error handling with detailed error messages
- **Timeout Protection**: Commands have timeout limits to prevent hangs

## Example Output

```
2025-10-19 18:36:07,915 - INFO - Starting Ubuntu System Repair Tool v32
2025-10-19 18:36:07,915 - INFO - Mode: DRY RUN
============================================================
STARTING SYSTEM ANALYSIS
============================================================
2025-10-19 18:36:07,915 - INFO - Checking disk space...
2025-10-19 18:36:07,916 - INFO - Disk space OK: 45% used
2025-10-19 18:36:07,916 - INFO - Checking critical services...
2025-10-19 18:36:07,916 - INFO - Service 'ssh' is active
...
============================================================
REPAIR REPORT
============================================================
Timestamp: 2025-10-19 18:36:16
Mode: DRY RUN

Issues Found:
  1. APT sources.list appears to be empty or all commented

Issues Fixed:
  1. Fixed broken packages and dependencies
  2. Cleaned package cache and removed unnecessary packages
  3. Restarted NetworkManager service
  4. Updated GRUB bootloader configuration
  5. Attempted to restart failed units
  6. Cleaned system logs
  7. Performed system optimization
============================================================
REPAIR PROCESS COMPLETED
============================================================
```

## Troubleshooting

### Permission Denied Errors
Make sure to run the script with sudo:
```bash
sudo python3 ubuntu_repair_ultimate_complete_v32.py
```

### Script Won't Execute
Ensure the script has execute permissions:
```bash
chmod +x ubuntu_repair_ultimate_complete_v32.py
```

### Testing Before Running
Always run with `--dry-run` first to see what would be done:
```bash
python3 ubuntu_repair_ultimate_complete_v32.py --dry-run --verbose
```

## Important Notes

- **Always backup important data** before running system repair tools
- The script requires root privileges for most operations (except dry-run mode)
- Some operations (like filesystem checks) may require a system reboot to complete
- The script is designed for Ubuntu systems but may work on other Debian-based distributions
- Review the log files after execution to understand what changes were made

## Contributing

If you find bugs or have suggestions for improvements, please submit an issue or pull request.

## License

This script is provided as-is for system maintenance purposes. Use at your own risk.

## Version History

- **v32**: Complete implementation with full functionality, no placeholders
  - Comprehensive system analysis
  - Full package management repairs
  - Network and bootloader fixes
  - System service management
  - Log cleanup and optimization
  - Detailed reporting and logging
