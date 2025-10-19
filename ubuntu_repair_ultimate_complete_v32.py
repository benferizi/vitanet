#!/usr/bin/env python3
"""
Ubuntu System Repair Ultimate Complete Script v32
A comprehensive system repair and maintenance tool for Ubuntu systems.
This script provides full implementations for various system repair operations.
"""

import os
import sys
import subprocess
import logging
import shutil
import time
import re
from datetime import datetime
from pathlib import Path
import argparse


class UbuntuRepairTool:
    """Comprehensive Ubuntu system repair and maintenance tool."""
    
    def __init__(self, dry_run=False, verbose=False):
        """Initialize the repair tool with configuration."""
        self.dry_run = dry_run
        self.verbose = verbose
        self.backup_dir = f"/tmp/ubuntu_repair_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.log_file = f"/tmp/ubuntu_repair_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        self.issues_found = []
        self.issues_fixed = []
        
        # Setup logging
        self._setup_logging()
        
        # Create backup directory
        if not self.dry_run:
            os.makedirs(self.backup_dir, exist_ok=True)
            self.log_info(f"Backup directory created: {self.backup_dir}")
    
    def _setup_logging(self):
        """Configure logging system."""
        log_format = '%(asctime)s - %(levelname)s - %(message)s'
        logging.basicConfig(
            level=logging.DEBUG if self.verbose else logging.INFO,
            format=log_format,
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def log_info(self, message):
        """Log informational message."""
        self.logger.info(message)
    
    def log_error(self, message):
        """Log error message."""
        self.logger.error(message)
    
    def log_warning(self, message):
        """Log warning message."""
        self.logger.warning(message)
    
    def run_command(self, command, check=True, capture_output=True):
        """Execute a shell command with error handling."""
        try:
            self.log_info(f"Executing: {' '.join(command) if isinstance(command, list) else command}")
            
            if self.dry_run:
                self.log_info("[DRY RUN] Command would be executed")
                return subprocess.CompletedProcess(command, 0, "", "")
            
            result = subprocess.run(
                command,
                check=check,
                capture_output=capture_output,
                text=True,
                timeout=300
            )
            
            if self.verbose and result.stdout:
                self.log_info(f"Output: {result.stdout[:500]}")
            
            return result
        except subprocess.CalledProcessError as e:
            self.log_error(f"Command failed: {e}")
            self.log_error(f"Error output: {e.stderr if hasattr(e, 'stderr') else 'N/A'}")
            if check:
                raise
            return e
        except subprocess.TimeoutExpired:
            self.log_error(f"Command timed out: {command}")
            raise
        except Exception as e:
            self.log_error(f"Unexpected error: {e}")
            raise
    
    def check_root_privileges(self):
        """Verify script is running with root privileges."""
        if os.geteuid() != 0 and not self.dry_run:
            self.log_error("This script requires root privileges. Please run with sudo.")
            sys.exit(1)
        self.log_info("Root privileges verified")
    
    def create_backup(self, file_path):
        """Create backup of a file before modification."""
        if not os.path.exists(file_path):
            self.log_warning(f"File does not exist for backup: {file_path}")
            return False
        
        try:
            backup_path = os.path.join(self.backup_dir, os.path.basename(file_path))
            if not self.dry_run:
                shutil.copy2(file_path, backup_path)
            self.log_info(f"Backup created: {backup_path}")
            return True
        except Exception as e:
            self.log_error(f"Failed to create backup: {e}")
            return False
    
    def analyze_system(self):
        """Perform comprehensive system analysis."""
        self.log_info("=" * 60)
        self.log_info("STARTING SYSTEM ANALYSIS")
        self.log_info("=" * 60)
        
        # Check disk space
        self._check_disk_space()
        
        # Check system load
        self._check_system_load()
        
        # Check critical services
        self._check_critical_services()
        
        # Check for broken packages
        self._check_broken_packages()
        
        # Check apt sources
        self._check_apt_sources()
        
        # Check system logs for errors
        self._check_system_logs()
        
        self.log_info(f"Analysis complete. Found {len(self.issues_found)} issues.")
        return self.issues_found
    
    def _check_disk_space(self):
        """Check available disk space."""
        self.log_info("Checking disk space...")
        try:
            result = self.run_command(['df', '-h', '/'], check=False)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    parts = lines[1].split()
                    if len(parts) >= 5:
                        usage = parts[4].rstrip('%')
                        if int(usage) > 90:
                            issue = f"Root partition is {usage}% full"
                            self.issues_found.append(issue)
                            self.log_warning(issue)
                        else:
                            self.log_info(f"Disk space OK: {usage}% used")
        except Exception as e:
            self.log_error(f"Error checking disk space: {e}")
    
    def _check_system_load(self):
        """Check system load average."""
        self.log_info("Checking system load...")
        try:
            with open('/proc/loadavg', 'r') as f:
                load = f.read().split()[0]
                self.log_info(f"System load average: {load}")
        except Exception as e:
            self.log_error(f"Error checking system load: {e}")
    
    def _check_critical_services(self):
        """Check status of critical system services."""
        self.log_info("Checking critical services...")
        critical_services = ['ssh', 'cron', 'rsyslog', 'systemd-journald']
        
        for service in critical_services:
            try:
                result = self.run_command(
                    ['systemctl', 'is-active', service],
                    check=False
                )
                if result.returncode != 0:
                    issue = f"Service '{service}' is not active"
                    self.issues_found.append(issue)
                    self.log_warning(issue)
                else:
                    self.log_info(f"Service '{service}' is active")
            except Exception as e:
                self.log_error(f"Error checking service {service}: {e}")
    
    def _check_broken_packages(self):
        """Check for broken or partially installed packages."""
        self.log_info("Checking for broken packages...")
        try:
            result = self.run_command(
                ['dpkg', '--audit'],
                check=False
            )
            if result.stdout.strip():
                issue = "Broken or partially installed packages detected"
                self.issues_found.append(issue)
                self.log_warning(issue)
                if self.verbose:
                    self.log_info(result.stdout)
            else:
                self.log_info("No broken packages found")
        except Exception as e:
            self.log_error(f"Error checking packages: {e}")
    
    def _check_apt_sources(self):
        """Check APT sources configuration."""
        self.log_info("Checking APT sources...")
        sources_file = '/etc/apt/sources.list'
        if os.path.exists(sources_file):
            try:
                with open(sources_file, 'r') as f:
                    content = f.read()
                    if not content.strip() or content.strip().startswith('#'):
                        issue = "APT sources.list appears to be empty or all commented"
                        self.issues_found.append(issue)
                        self.log_warning(issue)
                    else:
                        self.log_info("APT sources.list appears valid")
            except Exception as e:
                self.log_error(f"Error reading sources.list: {e}")
    
    def _check_system_logs(self):
        """Check system logs for critical errors."""
        self.log_info("Checking system logs...")
        try:
            result = self.run_command(
                ['journalctl', '-p', 'err', '-n', '50', '--no-pager'],
                check=False
            )
            if result.returncode == 0 and result.stdout.strip():
                error_count = len(result.stdout.strip().split('\n'))
                if error_count > 0:
                    issue = f"Found {error_count} recent error entries in system log"
                    self.issues_found.append(issue)
                    self.log_warning(issue)
        except Exception as e:
            self.log_error(f"Error checking system logs: {e}")
    
    def fix_dpkg_lock(self):
        """Fix dpkg/apt lock issues."""
        self.log_info("Checking for dpkg/apt lock issues...")
        
        lock_files = [
            '/var/lib/dpkg/lock',
            '/var/lib/dpkg/lock-frontend',
            '/var/lib/apt/lists/lock',
            '/var/cache/apt/archives/lock'
        ]
        
        locks_removed = False
        for lock_file in lock_files:
            if os.path.exists(lock_file):
                try:
                    # Check if any process is using the lock
                    result = self.run_command(
                        ['lsof', lock_file],
                        check=False
                    )
                    if result.returncode != 0:  # No process using the lock
                        self.log_info(f"Removing stale lock: {lock_file}")
                        if not self.dry_run:
                            os.remove(lock_file)
                        locks_removed = True
                except Exception as e:
                    self.log_error(f"Error handling lock file {lock_file}: {e}")
        
        if locks_removed:
            self.issues_fixed.append("Removed stale dpkg/apt locks")
        
        return locks_removed
    
    def fix_broken_packages(self):
        """Fix broken package dependencies."""
        self.log_info("Attempting to fix broken packages...")
        
        try:
            # Configure pending packages
            self.log_info("Configuring pending packages...")
            self.run_command(['dpkg', '--configure', '-a'], check=False)
            
            # Fix broken dependencies
            self.log_info("Fixing broken dependencies...")
            self.run_command(['apt-get', 'install', '-f', '-y'], check=False)
            
            # Update package lists
            self.log_info("Updating package lists...")
            self.run_command(['apt-get', 'update'], check=False)
            
            # Upgrade packages
            self.log_info("Upgrading packages...")
            self.run_command(['apt-get', 'upgrade', '-y'], check=False)
            
            self.issues_fixed.append("Fixed broken packages and dependencies")
            return True
        except Exception as e:
            self.log_error(f"Error fixing broken packages: {e}")
            return False
    
    def clean_package_cache(self):
        """Clean apt package cache."""
        self.log_info("Cleaning package cache...")
        
        try:
            # Remove retrieved package files
            self.run_command(['apt-get', 'clean'], check=False)
            
            # Remove old retrieved package files
            self.run_command(['apt-get', 'autoclean'], check=False)
            
            # Remove unnecessary packages
            self.run_command(['apt-get', 'autoremove', '-y'], check=False)
            
            self.issues_fixed.append("Cleaned package cache and removed unnecessary packages")
            return True
        except Exception as e:
            self.log_error(f"Error cleaning package cache: {e}")
            return False
    
    def check_filesystem(self):
        """Check filesystem for errors (read-only check)."""
        self.log_info("Checking filesystem status...")
        
        try:
            # Check if filesystem is mounted read-only
            result = self.run_command(['mount'], check=False)
            if 'ro,' in result.stdout:
                issue = "Filesystem mounted read-only detected"
                self.issues_found.append(issue)
                self.log_warning(issue)
                self.log_warning("Note: Filesystem checks require system reboot or remount")
            
            # Check filesystem statistics
            self.run_command(['df', '-i'], check=False)  # Check inodes
            
            return True
        except Exception as e:
            self.log_error(f"Error checking filesystem: {e}")
            return False
    
    def repair_network_config(self):
        """Repair network configuration."""
        self.log_info("Checking network configuration...")
        
        try:
            # Restart network manager
            self.log_info("Restarting NetworkManager...")
            result = self.run_command(
                ['systemctl', 'restart', 'NetworkManager'],
                check=False
            )
            
            if result.returncode == 0:
                self.issues_fixed.append("Restarted NetworkManager service")
            
            # Flush DNS cache
            self.log_info("Flushing DNS cache...")
            self.run_command(
                ['systemd-resolve', '--flush-caches'],
                check=False
            )
            
            return True
        except Exception as e:
            self.log_error(f"Error repairing network config: {e}")
            return False
    
    def fix_grub_bootloader(self):
        """Update and repair GRUB bootloader."""
        self.log_info("Checking GRUB bootloader...")
        
        try:
            # Update GRUB configuration
            self.log_info("Updating GRUB configuration...")
            result = self.run_command(['update-grub'], check=False)
            
            if result.returncode == 0:
                self.issues_fixed.append("Updated GRUB bootloader configuration")
                return True
            
            return False
        except Exception as e:
            self.log_error(f"Error fixing GRUB: {e}")
            return False
    
    def repair_system_services(self):
        """Restart failed system services."""
        self.log_info("Checking for failed services...")
        
        try:
            # Get list of failed services
            result = self.run_command(
                ['systemctl', 'list-units', '--failed', '--no-pager'],
                check=False
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                failed_services = [line.split()[0] for line in lines[1:-6] if line.strip()]
                
                if failed_services:
                    self.log_info(f"Found {len(failed_services)} failed services")
                    for service in failed_services:
                        self.log_info(f"Attempting to restart: {service}")
                        restart_result = self.run_command(
                            ['systemctl', 'restart', service],
                            check=False
                        )
                        if restart_result.returncode == 0:
                            self.log_info(f"Successfully restarted: {service}")
                else:
                    self.log_info("No failed services found")
                
                self.issues_fixed.append("Attempted to restart failed services")
                return True
            
            return False
        except Exception as e:
            self.log_error(f"Error repairing services: {e}")
            return False
    
    def clean_system_logs(self):
        """Clean old system logs."""
        self.log_info("Cleaning system logs...")
        
        try:
            # Rotate logs
            self.run_command(['logrotate', '-f', '/etc/logrotate.conf'], check=False)
            
            # Clean journal logs older than 7 days
            self.run_command(
                ['journalctl', '--vacuum-time=7d'],
                check=False
            )
            
            # Clean journal logs larger than 500M
            self.run_command(
                ['journalctl', '--vacuum-size=500M'],
                check=False
            )
            
            self.issues_fixed.append("Cleaned system logs")
            return True
        except Exception as e:
            self.log_error(f"Error cleaning logs: {e}")
            return False
    
    def optimize_system(self):
        """Perform system optimization tasks."""
        self.log_info("Performing system optimization...")
        
        try:
            # Update locate database
            self.log_info("Updating locate database...")
            self.run_command(['updatedb'], check=False)
            
            # Update man database
            self.log_info("Updating man database...")
            self.run_command(['mandb'], check=False)
            
            # Sync filesystem
            self.log_info("Syncing filesystem...")
            self.run_command(['sync'], check=False)
            
            self.issues_fixed.append("Performed system optimization")
            return True
        except Exception as e:
            self.log_error(f"Error during optimization: {e}")
            return False
    
    def generate_report(self):
        """Generate comprehensive repair report."""
        self.log_info("=" * 60)
        self.log_info("REPAIR REPORT")
        self.log_info("=" * 60)
        
        self.log_info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.log_info(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE'}")
        self.log_info(f"Log file: {self.log_file}")
        self.log_info(f"Backup directory: {self.backup_dir}")
        
        self.log_info("\nIssues Found:")
        if self.issues_found:
            for i, issue in enumerate(self.issues_found, 1):
                self.log_info(f"  {i}. {issue}")
        else:
            self.log_info("  No issues found")
        
        self.log_info("\nIssues Fixed:")
        if self.issues_fixed:
            for i, fix in enumerate(self.issues_fixed, 1):
                self.log_info(f"  {i}. {fix}")
        else:
            self.log_info("  No fixes applied")
        
        self.log_info("\n" + "=" * 60)
        self.log_info("REPAIR PROCESS COMPLETED")
        self.log_info("=" * 60)
        
        # Create report file
        report_file = f"/tmp/ubuntu_repair_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        try:
            with open(report_file, 'w') as f:
                f.write("Ubuntu System Repair Report\n")
                f.write("=" * 60 + "\n")
                f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE'}\n\n")
                
                f.write("Issues Found:\n")
                if self.issues_found:
                    for issue in self.issues_found:
                        f.write(f"  - {issue}\n")
                else:
                    f.write("  No issues found\n")
                
                f.write("\nIssues Fixed:\n")
                if self.issues_fixed:
                    for fix in self.issues_fixed:
                        f.write(f"  - {fix}\n")
                else:
                    f.write("  No fixes applied\n")
            
            self.log_info(f"Report saved to: {report_file}")
        except Exception as e:
            self.log_error(f"Error creating report file: {e}")
    
    def run_full_repair(self):
        """Execute complete repair process."""
        self.log_info("Starting Ubuntu System Repair Tool v32")
        self.log_info(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE'}")
        
        # Check privileges
        self.check_root_privileges()
        
        # Analyze system
        self.analyze_system()
        
        # Fix dpkg locks
        self.fix_dpkg_lock()
        
        # Fix broken packages
        self.fix_broken_packages()
        
        # Clean package cache
        self.clean_package_cache()
        
        # Check filesystem
        self.check_filesystem()
        
        # Repair network
        self.repair_network_config()
        
        # Fix GRUB
        self.fix_grub_bootloader()
        
        # Repair services
        self.repair_system_services()
        
        # Clean logs
        self.clean_system_logs()
        
        # Optimize system
        self.optimize_system()
        
        # Generate report
        self.generate_report()
        
        return len(self.issues_fixed) > 0


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description='Ubuntu System Repair Ultimate Complete Tool v32',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full repair (requires sudo)
  sudo python3 ubuntu_repair_ultimate_complete_v32.py

  # Dry run to see what would be done
  sudo python3 ubuntu_repair_ultimate_complete_v32.py --dry-run

  # Verbose output
  sudo python3 ubuntu_repair_ultimate_complete_v32.py --verbose

  # Dry run with verbose output
  sudo python3 ubuntu_repair_ultimate_complete_v32.py --dry-run --verbose
        """
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Perform dry run without making changes'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    # Create repair tool instance
    repair_tool = UbuntuRepairTool(
        dry_run=args.dry_run,
        verbose=args.verbose
    )
    
    try:
        # Run repair process
        success = repair_tool.run_full_repair()
        
        if success:
            sys.exit(0)
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        repair_tool.log_info("\nRepair process interrupted by user")
        sys.exit(130)
    except Exception as e:
        repair_tool.log_error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
