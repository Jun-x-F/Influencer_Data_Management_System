"""
@ProjectName: Influencer_Data_Management_System
@FileName：download_file.py
@IDE：PyCharm
@Author：Libre
@Time：2024/8/12 上午11:41
"""
from ast import main
import os
from spider.config.request_config import RequestConfig

# 获取当前脚本文件所在的目录
current_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
image_file_path = os.path.join(current_directory, 'static', 'image')


def download_image_file(image: str, file_name: str) -> str:
    """
    下载图片文件的方法
    
    Args:
        image: 图片URL
        file_name: 文件名
        
    Returns:
        str: 返回图片的URI地址
        
    Raises:
        Exception: 当下载失败时抛出异常
    """
    try:
        # 构建请求数据
        data = {
            "url": image,
            "image_name": file_name
        }
        
        # 使用RequestConfig发送POST请求
        response = RequestConfig.make_request(
            method='POST',
            url=f"{RequestConfig.BASE_URL}/api/file/download_image",
            json=data
        )
        
        # 解析响应数据
        response_data = response.json()
        data = response_data.get("data")

        if "uri" in data:
            return data['uri']
        else:
            raise Exception("下载失败：响应数据中没有uri字段")
            
    except Exception as e:
        raise Exception(f"下载失败：{str(e)}")

if __name__ == '__main__':
    print(download_image_file("http://172.16.11.245:5000/image/Tyler_Price.jpeg","Tyler_Price"))
