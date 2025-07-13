#!/usr/bin/env python3
"""
VitaNet Bundle CLI Tool
Command-line interface for VitaNet bundle operations.
"""

import sys
import argparse
import os
from bundle_manager import VitaNetBundleManager


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='VitaNet Bundle Management CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s create backup.vitanet --description "Daily backup"
  %(prog)s restore backup.vitanet --force
  %(prog)s info backup.vitanet
  %(prog)s status
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Create command
    create_parser = subparsers.add_parser('create', help='Create a VitaNet bundle')
    create_parser.add_argument('bundle_path', help='Path for the bundle file')
    create_parser.add_argument('--description', help='Bundle description')
    create_parser.add_argument('--db-path', default='vitanet.db', help='Database path (default: vitanet.db)')
    
    # Restore command
    restore_parser = subparsers.add_parser('restore', help='Restore from a VitaNet bundle')
    restore_parser.add_argument('bundle_path', help='Path to the bundle file')
    restore_parser.add_argument('--force', action='store_true', help='Overwrite existing database')
    restore_parser.add_argument('--db-path', default='vitanet.db', help='Database path (default: vitanet.db)')
    
    # Info command
    info_parser = subparsers.add_parser('info', help='Get information about a bundle')
    info_parser.add_argument('bundle_path', help='Path to the bundle file')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show current VitaNet status')
    status_parser.add_argument('--db-path', default='vitanet.db', help='Database path (default: vitanet.db)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Initialize bundle manager
    db_path = getattr(args, 'db_path', 'vitanet.db')
    manager = VitaNetBundleManager(db_path=db_path)
    
    try:
        if args.command == 'create':
            metadata = {}
            if args.description:
                metadata['description'] = args.description
            
            result = manager.create_bundle(args.bundle_path, metadata)
            
            if result['success']:
                print(f"✓ Bundle created successfully: {result['bundle_path']}")
                print(f"  Size: {result['bundle_size']} bytes")
                print(f"  Database included: {result['metadata']['database_included']}")
                if metadata:
                    print(f"  Metadata: {metadata}")
            else:
                print(f"✗ Failed to create bundle: {result['message']}")
                return 1
        
        elif args.command == 'restore':
            result = manager.restore_bundle(args.bundle_path, force=args.force)
            
            if result['success']:
                print(f"✓ Bundle restored successfully from: {args.bundle_path}")
                print(f"  Restored from: {result['restored_from']}")
                if result.get('backup_created'):
                    print(f"  Backup created: {result['backup_path']}")
                print(f"  Bundle created: {result['metadata']['created_at']}")
            else:
                print(f"✗ Failed to restore bundle: {result['message']}")
                return 1
        
        elif args.command == 'info':
            result = manager.list_bundle_info(args.bundle_path)
            
            if result['success']:
                print(f"Bundle Information: {args.bundle_path}")
                print(f"  Size: {result['bundle_size']} bytes")
                print(f"  Version: {result['metadata']['version']}")
                print(f"  Created: {result['metadata']['created_at']}")
                print(f"  Database included: {result['metadata']['database_included']}")
                print(f"  Contents: {', '.join(result['contents'])}")
                
                if result['metadata'].get('custom_metadata'):
                    print("  Custom metadata:")
                    for key, value in result['metadata']['custom_metadata'].items():
                        print(f"    {key}: {value}")
            else:
                print(f"✗ Failed to read bundle: {result['message']}")
                return 1
        
        elif args.command == 'status':
            db_exists = os.path.exists(manager.db_path)
            db_size = os.path.getsize(manager.db_path) if db_exists else 0
            
            print("VitaNet Status:")
            print(f"  Database path: {manager.db_path}")
            print(f"  Database exists: {'Yes' if db_exists else 'No'}")
            if db_exists:
                print(f"  Database size: {db_size} bytes")
            print(f"  Bundle version: {manager.BUNDLE_VERSION}")
            print(f"  Bundle extension: {manager.BUNDLE_EXTENSION}")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n✗ Operation cancelled by user")
        return 1
    except Exception as e:
        print(f"✗ Unexpected error: {str(e)}")
        return 1


if __name__ == '__main__':
    sys.exit(main())