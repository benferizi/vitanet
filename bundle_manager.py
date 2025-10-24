"""
VitaNet Bundle Manager
Handles creation and restoration of VitaNet bundles.
A bundle contains database data, configuration, and metadata.
"""

import json
import os
import sqlite3
import zipfile
import tempfile
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import shutil


class VitaNetBundleManager:
    """Manages VitaNet bundle creation and restoration operations."""
    
    BUNDLE_VERSION = "1.0"
    BUNDLE_EXTENSION = ".vitanet"
    
    def __init__(self, db_path: str = "vitanet.db"):
        """Initialize the bundle manager with database path."""
        self.db_path = db_path
        
    def create_bundle(self, bundle_path: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a VitaNet bundle containing database and configuration.
        
        Args:
            bundle_path: Path where the bundle file should be created
            metadata: Optional metadata to include in the bundle
            
        Returns:
            Dict containing bundle creation results
        """
        try:
            # Ensure bundle path has correct extension
            if not bundle_path.endswith(self.BUNDLE_EXTENSION):
                bundle_path += self.BUNDLE_EXTENSION
                
            # Create temporary directory for bundle contents
            with tempfile.TemporaryDirectory() as temp_dir:
                # Create bundle metadata
                bundle_metadata = {
                    "version": self.BUNDLE_VERSION,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "vitanet_version": "1.0",
                    "database_included": os.path.exists(self.db_path),
                    "custom_metadata": metadata or {}
                }
                
                # Save metadata to temp directory
                metadata_path = os.path.join(temp_dir, "bundle_metadata.json")
                with open(metadata_path, 'w') as f:
                    json.dump(bundle_metadata, f, indent=2)
                
                # Copy database if it exists
                db_backup_path = None
                if os.path.exists(self.db_path):
                    db_backup_path = os.path.join(temp_dir, "vitanet_backup.db")
                    shutil.copy2(self.db_path, db_backup_path)
                
                # Export database schema and data
                if os.path.exists(self.db_path):
                    schema_path = os.path.join(temp_dir, "schema.sql")
                    data_path = os.path.join(temp_dir, "data.sql")
                    self._export_database_sql(schema_path, data_path)
                
                # Create the bundle zip file
                with zipfile.ZipFile(bundle_path, 'w', zipfile.ZIP_DEFLATED) as bundle_zip:
                    # Add metadata
                    bundle_zip.write(metadata_path, "bundle_metadata.json")
                    
                    # Add database files if they exist
                    if db_backup_path and os.path.exists(db_backup_path):
                        bundle_zip.write(db_backup_path, "vitanet_backup.db")
                    
                    if os.path.exists(os.path.join(temp_dir, "schema.sql")):
                        bundle_zip.write(os.path.join(temp_dir, "schema.sql"), "schema.sql")
                    
                    if os.path.exists(os.path.join(temp_dir, "data.sql")):
                        bundle_zip.write(os.path.join(temp_dir, "data.sql"), "data.sql")
                
                return {
                    "success": True,
                    "bundle_path": bundle_path,
                    "bundle_size": os.path.getsize(bundle_path),
                    "metadata": bundle_metadata,
                    "message": f"Bundle created successfully at {bundle_path}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to create bundle: {str(e)}"
            }
    
    def restore_bundle(self, bundle_path: str, force: bool = False) -> Dict[str, Any]:
        """
        Restore VitaNet from a bundle file.
        
        Args:
            bundle_path: Path to the bundle file
            force: Whether to overwrite existing database
            
        Returns:
            Dict containing restoration results
        """
        try:
            if not os.path.exists(bundle_path):
                return {
                    "success": False,
                    "error": "Bundle file not found",
                    "message": f"Bundle file {bundle_path} does not exist"
                }
            
            # Check if database exists and force is not set
            if os.path.exists(self.db_path) and not force:
                return {
                    "success": False,
                    "error": "Database exists",
                    "message": "Database already exists. Use force=True to overwrite"
                }
            
            # Create temporary directory for extraction
            with tempfile.TemporaryDirectory() as temp_dir:
                # Extract bundle
                with zipfile.ZipFile(bundle_path, 'r') as bundle_zip:
                    bundle_zip.extractall(temp_dir)
                
                # Read metadata
                metadata_path = os.path.join(temp_dir, "bundle_metadata.json")
                if not os.path.exists(metadata_path):
                    return {
                        "success": False,
                        "error": "Invalid bundle",
                        "message": "Bundle metadata not found"
                    }
                
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                
                # Validate bundle version
                if metadata.get("version") != self.BUNDLE_VERSION:
                    return {
                        "success": False,
                        "error": "Version mismatch",
                        "message": f"Bundle version {metadata.get('version')} not supported"
                    }
                
                # Backup existing database if it exists
                backup_created = False
                if os.path.exists(self.db_path):
                    backup_path = f"{self.db_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    shutil.copy2(self.db_path, backup_path)
                    backup_created = True
                
                # Restore database
                restored_from = None
                db_backup_path = os.path.join(temp_dir, "vitanet_backup.db")
                schema_path = os.path.join(temp_dir, "schema.sql")
                data_path = os.path.join(temp_dir, "data.sql")
                
                if os.path.exists(db_backup_path):
                    # Restore from backup database file
                    shutil.copy2(db_backup_path, self.db_path)
                    restored_from = "backup_database"
                elif os.path.exists(schema_path):
                    # Restore from SQL files
                    self._restore_from_sql(schema_path, data_path)
                    restored_from = "sql_files"
                else:
                    # Create empty database
                    self._create_empty_database()
                    restored_from = "empty_database"
                
                result = {
                    "success": True,
                    "bundle_path": bundle_path,
                    "restored_from": restored_from,
                    "metadata": metadata,
                    "backup_created": backup_created,
                    "message": "Bundle restored successfully"
                }
                
                if backup_created:
                    result["backup_path"] = backup_path
                
                return result
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to restore bundle: {str(e)}"
            }
    
    def list_bundle_info(self, bundle_path: str) -> Dict[str, Any]:
        """
        Get information about a bundle without restoring it.
        
        Args:
            bundle_path: Path to the bundle file
            
        Returns:
            Dict containing bundle information
        """
        try:
            if not os.path.exists(bundle_path):
                return {
                    "success": False,
                    "error": "Bundle file not found",
                    "message": f"Bundle file {bundle_path} does not exist"
                }
            
            with tempfile.TemporaryDirectory() as temp_dir:
                with zipfile.ZipFile(bundle_path, 'r') as bundle_zip:
                    # Extract only metadata
                    bundle_zip.extract("bundle_metadata.json", temp_dir)
                    
                    # Get bundle contents
                    bundle_contents = bundle_zip.namelist()
                
                metadata_path = os.path.join(temp_dir, "bundle_metadata.json")
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                
                return {
                    "success": True,
                    "bundle_path": bundle_path,
                    "bundle_size": os.path.getsize(bundle_path),
                    "metadata": metadata,
                    "contents": bundle_contents,
                    "message": "Bundle information retrieved successfully"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to read bundle: {str(e)}"
            }
    
    def _export_database_sql(self, schema_path: str, data_path: str) -> None:
        """Export database schema and data to SQL files."""
        if not os.path.exists(self.db_path):
            return
            
        conn = sqlite3.connect(self.db_path)
        
        # Export schema
        with open(schema_path, 'w') as f:
            for line in conn.iterdump():
                if line.startswith('CREATE') or line.startswith('INSERT') == False:
                    f.write(line + '\n')
                if line.startswith('INSERT'):
                    break
        
        # Export data
        with open(data_path, 'w') as f:
            for line in conn.iterdump():
                if line.startswith('INSERT'):
                    f.write(line + '\n')
        
        conn.close()
    
    def _restore_from_sql(self, schema_path: str, data_path: str) -> None:
        """Restore database from SQL files."""
        # Remove existing database
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        
        conn = sqlite3.connect(self.db_path)
        
        # Restore schema
        if os.path.exists(schema_path):
            with open(schema_path, 'r') as f:
                conn.executescript(f.read())
        
        # Restore data
        if os.path.exists(data_path):
            with open(data_path, 'r') as f:
                conn.executescript(f.read())
        
        conn.close()
    
    def _create_empty_database(self) -> None:
        """Create an empty database with basic structure."""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
            
        conn = sqlite3.connect(self.db_path)
        # Create basic tables if needed
        conn.execute('''
            CREATE TABLE IF NOT EXISTS vitanet_info (
                id INTEGER PRIMARY KEY,
                key TEXT UNIQUE,
                value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insert version info
        conn.execute('''
            INSERT OR REPLACE INTO vitanet_info (key, value) 
            VALUES ('version', '1.0')
        ''')
        
        conn.commit()
        conn.close()