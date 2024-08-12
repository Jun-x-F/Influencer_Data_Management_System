"""
@ProjectName: Influencer_Data_Management_System
@FileName：get_file.py
@IDE：PyCharm
@Author：Libre
@Time：2024/8/12 下午1:43
"""
import os.path

from flask import Blueprint, send_file, abort

from tool.download_file import image_file_path

image_bp = Blueprint('image', __name__)


@image_bp.route('/<image_name>')
def get_image(image_name):
    try:
        path = os.path.join(image_file_path, image_name)
        mimetype = "image/jpeg"
        return send_file(str(path), mimetype=mimetype)
    except Exception as e:
        abort(404, description="Image not found")
