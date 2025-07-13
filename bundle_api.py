"""
VitaNet Bundle API Blueprint
Provides REST API endpoints for bundle operations.
"""

from flask import Blueprint, request, jsonify, send_file
import os
import tempfile
from bundle_manager import VitaNetBundleManager

# Create blueprint
bundle_bp = Blueprint('bundle', __name__, url_prefix='/api/bundle')

# Initialize bundle manager
bundle_manager = VitaNetBundleManager()


@bundle_bp.route('/create', methods=['POST'])
def create_bundle():
    """
    Create a new VitaNet bundle.
    
    Request JSON:
    {
        "filename": "optional_custom_filename",
        "metadata": {
            "description": "Optional description",
            "tags": ["tag1", "tag2"]
        }
    }
    """
    try:
        data = request.get_json() or {}
        
        # Generate filename
        filename = data.get('filename', f"vitanet_bundle_{bundle_manager._get_timestamp()}")
        if not filename.endswith(bundle_manager.BUNDLE_EXTENSION):
            filename += bundle_manager.BUNDLE_EXTENSION
        
        # Create bundle in temp directory
        with tempfile.TemporaryDirectory() as temp_dir:
            bundle_path = os.path.join(temp_dir, filename)
            metadata = data.get('metadata', {})
            
            result = bundle_manager.create_bundle(bundle_path, metadata)
            
            if result['success']:
                # Return the bundle file
                return send_file(
                    bundle_path,
                    as_attachment=True,
                    download_name=filename,
                    mimetype='application/zip'
                )
            else:
                return jsonify(result), 400
                
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': f'Failed to create bundle: {str(e)}'
        }), 500


@bundle_bp.route('/restore', methods=['POST'])
def restore_bundle():
    """
    Restore VitaNet from an uploaded bundle.
    
    Form data:
    - bundle_file: The bundle file to restore from
    - force: Whether to overwrite existing database (optional, default: false)
    """
    try:
        if 'bundle_file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No bundle file provided',
                'message': 'Please upload a bundle file'
            }), 400
        
        bundle_file = request.files['bundle_file']
        if bundle_file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected',
                'message': 'Please select a bundle file'
            }), 400
        
        # Check file extension
        if not bundle_file.filename.endswith(bundle_manager.BUNDLE_EXTENSION):
            return jsonify({
                'success': False,
                'error': 'Invalid file type',
                'message': f'Bundle file must have {bundle_manager.BUNDLE_EXTENSION} extension'
            }), 400
        
        # Get force parameter
        force = request.form.get('force', 'false').lower() == 'true'
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=bundle_manager.BUNDLE_EXTENSION) as temp_file:
            bundle_file.save(temp_file.name)
            
            try:
                result = bundle_manager.restore_bundle(temp_file.name, force=force)
                return jsonify(result), 200 if result['success'] else 400
            finally:
                # Clean up temporary file
                os.unlink(temp_file.name)
                
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': f'Failed to restore bundle: {str(e)}'
        }), 500


@bundle_bp.route('/info', methods=['POST'])
def bundle_info():
    """
    Get information about an uploaded bundle without restoring it.
    
    Form data:
    - bundle_file: The bundle file to examine
    """
    try:
        if 'bundle_file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No bundle file provided',
                'message': 'Please upload a bundle file'
            }), 400
        
        bundle_file = request.files['bundle_file']
        if bundle_file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected',
                'message': 'Please select a bundle file'
            }), 400
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=bundle_manager.BUNDLE_EXTENSION) as temp_file:
            bundle_file.save(temp_file.name)
            
            try:
                result = bundle_manager.list_bundle_info(temp_file.name)
                return jsonify(result), 200 if result['success'] else 400
            finally:
                # Clean up temporary file
                os.unlink(temp_file.name)
                
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': f'Failed to read bundle: {str(e)}'
        }), 500


@bundle_bp.route('/status', methods=['GET'])
def bundle_status():
    """
    Get current VitaNet database status and bundle capabilities.
    """
    try:
        db_exists = os.path.exists(bundle_manager.db_path)
        db_size = os.path.getsize(bundle_manager.db_path) if db_exists else 0
        
        status = {
            'success': True,
            'database_exists': db_exists,
            'database_path': bundle_manager.db_path,
            'database_size': db_size,
            'bundle_version': bundle_manager.BUNDLE_VERSION,
            'bundle_extension': bundle_manager.BUNDLE_EXTENSION,
            'can_create_bundle': True,
            'can_restore_bundle': True,
            'message': 'Bundle status retrieved successfully'
        }
        
        return jsonify(status), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': f'Failed to get bundle status: {str(e)}'
        }), 500


# Add helper method to bundle manager
def _get_timestamp(self):
    """Get current timestamp for filenames."""
    from datetime import datetime
    return datetime.now().strftime('%Y%m%d_%H%M%S')

VitaNetBundleManager._get_timestamp = _get_timestamp