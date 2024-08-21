"""
@ProjectName: Influencer_Data_Management_System
@FileName：config.py
@IDE：PyCharm
@Author：Libre
@Time：2024/8/16 下午3:01
"""
import random

from log.logger import global_log
from spider.sql.redisConn import RedisClient
from spider.template.class_dict_template import FIFODict

# 是否打开页面
headerLess = True

# user_agent
user_agent = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 "
              "Safari/537.36")


# 模拟随机窗口大小
def return_viewPort():
    return {'width': random.randint(1280, 1920), 'height': random.randint(720, 1080)}


global_log.info(f"初始化爬虫配置文件，页面关闭展示为：{headerLess}，user_agent为：{user_agent}")

# 用于存储用户提交的视频链接
submitted_video_links = FIFODict()
# 用于存储用户提交的物流订单链接
order_links = FIFODict()
# 用于存储用户提交的红人链接
submitted_influencer_links = FIFODict()
# 提交视频异常
submitted_one_video_error = False
# 视频在7天之内，不需要执行其他任务
submitted_pass_video = None

global_log.info(f"初始化线程队列，检查redis连接")

# redis连接
redis_conn = RedisClient(host='172.16.11.245', port=6379, db=3)


