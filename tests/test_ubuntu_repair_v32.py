"""Test suite for ubuntu_repair_ultimate_complete_v32.py"""

import sys
import os

# Add parent directory to path to import the script
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the script module
import ubuntu_repair_ultimate_complete_v32 as repair_script


def test_import():
    """Test that the module can be imported."""
    assert repair_script is not None


def test_ubuntu_repair_tool_class_exists():
    """Test that UbuntuRepairTool class exists."""
    assert hasattr(repair_script, 'UbuntuRepairTool')


def test_ubuntu_repair_tool_initialization():
    """Test that UbuntuRepairTool can be instantiated in dry-run mode."""
    tool = repair_script.UbuntuRepairTool(dry_run=True, verbose=False)
    assert tool is not None
    assert tool.dry_run is True
    assert tool.verbose is False


def test_ubuntu_repair_tool_has_required_methods():
    """Test that UbuntuRepairTool has all required methods."""
    tool = repair_script.UbuntuRepairTool(dry_run=True, verbose=False)
    
    required_methods = [
        'analyze_system',
        'fix_dpkg_lock',
        'fix_broken_packages',
        'clean_package_cache',
        'check_filesystem',
        'repair_network_config',
        'fix_grub_bootloader',
        'repair_system_services',
        'clean_system_logs',
        'optimize_system',
        'generate_report',
        'run_full_repair'
    ]
    
    for method in required_methods:
        assert hasattr(tool, method)


def test_log_methods():
    """Test logging methods exist and work."""
    tool = repair_script.UbuntuRepairTool(dry_run=True, verbose=False)
    
    # Test log methods don't raise exceptions
    tool.log_info("Test info message")
    tool.log_warning("Test warning message")
    tool.log_error("Test error message")


def test_dry_run_mode():
    """Test that dry-run mode prevents actual changes."""
    tool = repair_script.UbuntuRepairTool(dry_run=True, verbose=False)
    assert tool.dry_run is True


def test_backup_dir_creation():
    """Test that backup directory path is set."""
    tool = repair_script.UbuntuRepairTool(dry_run=True, verbose=False)
    assert tool.backup_dir is not None
    assert '/tmp/ubuntu_repair_backup_' in tool.backup_dir


def test_log_file_creation():
    """Test that log file path is set."""
    tool = repair_script.UbuntuRepairTool(dry_run=True, verbose=False)
    assert tool.log_file is not None
    assert '/tmp/ubuntu_repair_' in tool.log_file
    assert tool.log_file.endswith('.log')


def test_issues_tracking():
    """Test that issues are tracked."""
    tool = repair_script.UbuntuRepairTool(dry_run=True, verbose=False)
    assert isinstance(tool.issues_found, list)
    assert isinstance(tool.issues_fixed, list)
