from flask import Blueprint, jsonify

vitalsync_bp = Blueprint('vitalsync', __name__)


@vitalsync_bp.route('/vitalsync', methods=['GET'])
def vitalsync_home():
    return jsonify({
        'message': 'Welcome to VitalsSync Module!'
    })
