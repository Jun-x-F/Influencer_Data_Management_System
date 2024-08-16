"""
@ProjectName: Influencer_Data_Management_System
@FileName：config.py
@IDE：PyCharm
@Author：Libre
@Time：2024/8/16 下午3:01
"""
import random

from log.logger import global_log
from spider.template.class_dict_template import FIFODict

# 是否打开页面
headerLess = False

# user_agent
user_agent = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 "
              "Safari/537.36")


# 模拟随机窗口大小
def return_viewPort():
    return {'width': random.randint(1280, 1920), 'height': random.randint(720, 1080)}


global_log.info(f"初始化配置文件，页面关闭展示为：{headerLess}")

# 用于存储用户提交的视频链接
submitted_video_links = FIFODict()
# 用于存储用户提交的物流订单链接
order_links = FIFODict()
# 用于存储用户提交的红人链接
submitted_influencer_links = FIFODict()
