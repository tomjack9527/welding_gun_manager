# welding_gun_manager/controllers/download_controller.py

import os
from flask import send_file, jsonify

UPLOAD_FOLDER = 'uploads/'

def download_file(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return jsonify({'error': 'File not found'}), 404