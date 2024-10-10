"""
@ProjectName: Influencer_Data_Management_System
@FileName：get_file.py
@IDE：PyCharm
@Author：Libre
@Time：2024/8/12 下午1:43
"""
import io
import os.path

from PIL import Image
from flask import Blueprint, send_file

from tool.download_file import image_file_path

image_bp = Blueprint('image', __name__)


@image_bp.route('/<image_name>')
def get_image(image_name):
    try:
        path = os.path.join(image_file_path, image_name)
        mimetype = "image/jpeg"
        # 缓存一天
        return send_file(str(path), mimetype=mimetype, max_age=86400)
    except Exception as e:
        # abort(404, description="Image not found")
        # 创建一个空白图像
        img = Image.new('RGB', (300, 300), color='white')  # 设置长宽高一致
        img_io = io.BytesIO()
        img.save(img_io, 'JPEG')
        img_io.seek(0)
        return send_file(img_io, mimetype='image/jpeg', max_age=86400)
