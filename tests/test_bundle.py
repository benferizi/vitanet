"""
Test suite for VitaNet Bundle functionality.
Tests bundle creation, restoration, and API endpoints.
"""

import pytest
import tempfile
import os
import json
import zipfile
import shutil
from unittest.mock import patch
import sqlite3

# Import the modules to test
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bundle_manager import VitaNetBundleManager

# Import Flask app directly from app.py file
import importlib.util
spec = importlib.util.spec_from_file_location("app_main", "app.py")
app_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app_module)


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    # Get the Flask app object from app.py
    flask_app = app_module.app
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        yield client


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    # Create a test database with some data
    conn = sqlite3.connect(db_path)
    conn.execute('''
        CREATE TABLE test_table (
            id INTEGER PRIMARY KEY,
            name TEXT,
            value INTEGER
        )
    ''')
    conn.execute("INSERT INTO test_table (name, value) VALUES ('test1', 100)")
    conn.execute("INSERT INTO test_table (name, value) VALUES ('test2', 200)")
    conn.commit()
    conn.close()
    
    yield db_path
    
    # Cleanup
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture
def bundle_manager(temp_db):
    """Create a bundle manager with a temporary database."""
    return VitaNetBundleManager(db_path=temp_db)


class TestVitaNetBundleManager:
    """Test the VitaNetBundleManager class."""
    
    def test_create_bundle_success(self, bundle_manager, temp_db):
        """Test successful bundle creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            bundle_path = os.path.join(temp_dir, "test_bundle")
            metadata = {"description": "Test bundle", "version": "1.0"}
            
            result = bundle_manager.create_bundle(bundle_path, metadata)
            
            assert result['success'] is True
            assert os.path.exists(bundle_path + bundle_manager.BUNDLE_EXTENSION)
            assert 'bundle_size' in result
            assert result['metadata']['version'] == bundle_manager.BUNDLE_VERSION
            assert result['metadata']['custom_metadata'] == metadata
    
    def test_create_bundle_no_database(self):
        """Test bundle creation when no database exists."""
        manager = VitaNetBundleManager(db_path="nonexistent.db")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            bundle_path = os.path.join(temp_dir, "test_bundle")
            
            result = manager.create_bundle(bundle_path)
            
            assert result['success'] is True
            assert result['metadata']['database_included'] is False
    
    def test_restore_bundle_success(self, bundle_manager, temp_db):
        """Test successful bundle restoration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a bundle first
            bundle_path = os.path.join(temp_dir, "test_bundle")
            create_result = bundle_manager.create_bundle(bundle_path)
            assert create_result['success'] is True
            
            # Create a new database path for restoration
            restore_db_path = os.path.join(temp_dir, "restored.db")
            restore_manager = VitaNetBundleManager(db_path=restore_db_path)
            
            # Restore the bundle
            restore_result = restore_manager.restore_bundle(bundle_path + bundle_manager.BUNDLE_EXTENSION)
            
            assert restore_result['success'] is True
            assert os.path.exists(restore_db_path)
            assert 'metadata' in restore_result
    
    def test_restore_bundle_force_overwrite(self, bundle_manager, temp_db):
        """Test bundle restoration with force overwrite."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a bundle
            bundle_path = os.path.join(temp_dir, "test_bundle")
            create_result = bundle_manager.create_bundle(bundle_path)
            assert create_result['success'] is True
            
            # Try to restore to existing database without force
            result_no_force = bundle_manager.restore_bundle(bundle_path + bundle_manager.BUNDLE_EXTENSION)
            assert result_no_force['success'] is False
            assert "Database exists" in result_no_force['error']
            
            # Restore with force
            result_force = bundle_manager.restore_bundle(bundle_path + bundle_manager.BUNDLE_EXTENSION, force=True)
            assert result_force['success'] is True
            assert result_force['backup_created'] is True
    
    def test_restore_bundle_nonexistent_file(self, bundle_manager):
        """Test restoration of non-existent bundle file."""
        result = bundle_manager.restore_bundle("nonexistent_bundle.vitanet")
        
        assert result['success'] is False
        assert "Bundle file not found" in result['error']
    
    def test_list_bundle_info(self, bundle_manager, temp_db):
        """Test getting bundle information."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a bundle
            bundle_path = os.path.join(temp_dir, "test_bundle")
            metadata = {"description": "Test bundle info", "author": "test"}
            create_result = bundle_manager.create_bundle(bundle_path, metadata)
            assert create_result['success'] is True
            
            # Get bundle info
            info_result = bundle_manager.list_bundle_info(bundle_path + bundle_manager.BUNDLE_EXTENSION)
            
            assert info_result['success'] is True
            assert 'metadata' in info_result
            assert info_result['metadata']['custom_metadata'] == metadata
            assert 'contents' in info_result
            assert 'bundle_metadata.json' in info_result['contents']
    
    def test_bundle_version_validation(self, bundle_manager):
        """Test bundle version validation during restoration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a fake bundle with wrong version
            bundle_path = os.path.join(temp_dir, "invalid_bundle.vitanet")
            
            # Create metadata with wrong version
            metadata = {
                "version": "0.1",  # Wrong version
                "created_at": "2024-01-01T00:00:00",
                "vitanet_version": "1.0"
            }
            
            with zipfile.ZipFile(bundle_path, 'w') as bundle_zip:
                metadata_str = json.dumps(metadata)
                bundle_zip.writestr("bundle_metadata.json", metadata_str)
            
            # Try to restore with force to bypass database existence check
            result = bundle_manager.restore_bundle(bundle_path, force=True)
            
            assert result['success'] is False
            assert "Version mismatch" in result['error']


class TestBundleAPI:
    """Test the Bundle REST API endpoints."""
    
    def test_bundle_status_endpoint(self, client):
        """Test the bundle status endpoint."""
        response = client.get('/api/bundle/status')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'bundle_version' in data
        assert 'bundle_extension' in data
        assert 'can_create_bundle' in data
    
    def test_create_bundle_endpoint(self, client):
        """Test the create bundle endpoint."""
        # Mock the database to exist
        with patch('bundle_manager.os.path.exists', return_value=True):
            response = client.post('/api/bundle/create', 
                                 json={'metadata': {'description': 'API test bundle'}})
            
            # Should return the bundle file
            assert response.status_code == 200
            assert response.mimetype == 'application/zip'
    
    def test_bundle_info_endpoint(self, client, bundle_manager, temp_db):
        """Test the bundle info endpoint with file upload."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a test bundle
            bundle_path = os.path.join(temp_dir, "test_bundle.vitanet")
            result = bundle_manager.create_bundle(bundle_path)
            assert result['success'] is True
            
            # Test the info endpoint
            with open(bundle_path, 'rb') as bundle_file:
                response = client.post('/api/bundle/info',
                                     data={'bundle_file': bundle_file})
                
                assert response.status_code == 200
                data = json.loads(response.data)
                assert data['success'] is True
                assert 'metadata' in data
    
    def test_restore_bundle_endpoint_no_file(self, client):
        """Test restore endpoint without uploading a file."""
        response = client.post('/api/bundle/restore')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'No bundle file provided' in data['error']
    
    def test_restore_bundle_endpoint_invalid_extension(self, client):
        """Test restore endpoint with invalid file extension."""
        with tempfile.NamedTemporaryFile(suffix='.txt') as temp_file:
            temp_file.write(b'fake content')
            temp_file.seek(0)
            
            response = client.post('/api/bundle/restore',
                                 data={'bundle_file': (temp_file, 'test.txt')})
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['success'] is False
            assert 'Invalid file type' in data['error']


class TestBundleIntegration:
    """Integration tests for the complete bundle workflow."""
    
    def test_complete_bundle_workflow(self, bundle_manager, temp_db):
        """Test the complete create -> restore workflow."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Step 1: Create a bundle
            bundle_path = os.path.join(temp_dir, "workflow_test")
            metadata = {"test": "complete_workflow", "step": 1}
            
            create_result = bundle_manager.create_bundle(bundle_path, metadata)
            assert create_result['success'] is True
            
            bundle_file = bundle_path + bundle_manager.BUNDLE_EXTENSION
            assert os.path.exists(bundle_file)
            
            # Step 2: Get bundle info
            info_result = bundle_manager.list_bundle_info(bundle_file)
            assert info_result['success'] is True
            assert info_result['metadata']['custom_metadata'] == metadata
            
            # Step 3: Create new database location and restore
            new_db_path = os.path.join(temp_dir, "restored.db")
            new_manager = VitaNetBundleManager(db_path=new_db_path)
            
            restore_result = new_manager.restore_bundle(bundle_file)
            assert restore_result['success'] is True
            assert os.path.exists(new_db_path)
            
            # Step 4: Verify restored data
            conn = sqlite3.connect(new_db_path)
            cursor = conn.execute("SELECT name, value FROM test_table ORDER BY id")
            rows = cursor.fetchall()
            conn.close()
            
            # Should have the original test data
            assert len(rows) == 2
            assert rows[0] == ('test1', 100)
            assert rows[1] == ('test2', 200)
    
    def test_bundle_validation_and_error_handling(self, bundle_manager):
        """Test various error conditions and validation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test with empty zip file
            empty_bundle = os.path.join(temp_dir, "empty.vitanet")
            with zipfile.ZipFile(empty_bundle, 'w'):
                pass  # Create empty zip
            
            result = bundle_manager.restore_bundle(empty_bundle, force=True)
            assert result['success'] is False
            assert "Invalid bundle" in result['error']
            
            # Test with corrupted zip
            corrupted_bundle = os.path.join(temp_dir, "corrupted.vitanet")
            with open(corrupted_bundle, 'wb') as f:
                f.write(b'not a zip file')
            
            result = bundle_manager.restore_bundle(corrupted_bundle, force=True)
            assert result['success'] is False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])