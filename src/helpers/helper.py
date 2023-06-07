import os
from flask import jsonify, send_from_directory


def get_image(file_name):
    image_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'images')

    # Check if the file exists in the directory
    file_path = os.path.join(image_dir, file_name)

    # Check if the directory exists
    if not os.path.isdir(image_dir):
        return jsonify({"error": "Image directory not found"}), 404

    # Check if the file exists
    if not os.path.isfile(file_path):
        return jsonify({"error": "Image not found"}), 404

    # Serve the image file
    return send_from_directory(image_dir, file_name)
