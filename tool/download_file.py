"""
@ProjectName: Influencer_Data_Management_System
@FileName：download_file.py
@IDE：PyCharm
@Author：Libre
@Time：2024/8/12 上午11:41
"""
import os

import requests

# 获取当前脚本文件所在的目录
current_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
image_file_path = os.path.join(current_directory, 'static', 'image')


def download_image_file(image: str, file_name: str):
    response = requests.get(image, stream=True)
    # 检查请求是否成功
    if response.status_code == 200:
        with open(os.path.join(image_file_path, file_name+".jpeg"), 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
    else:
        raise "下载失败"
