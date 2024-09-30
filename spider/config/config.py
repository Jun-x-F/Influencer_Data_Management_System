"""
@ProjectName: Influencer_Data_Management_System
@FileName：config.py
@IDE：PyCharm
@Author：Libre
@Time：2024/8/16 下午3:01
"""
import os
import random

from log.logger import global_log
from spider.sql.redisConn import RedisClient
from spider.template.class_dict_template import FIFODict
from spider.template.class_message_queue_template import Notice
from tool.FileUtils import get_project_path

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
# 不执行物流信息
submitted_pass_track = False
# 视频在7天之内，不需要执行其他任务
submitted_pass_video = False

global_log.info(f"初始化线程队列，检查redis连接")

# redis连接
redis_conn = RedisClient(host='172.16.11.245', port=6379, db=3)

# 消息队列超时时间/秒
message_timeout = 5 * 60
message_queue = Notice(message_timeout)

global_log.info(f"初始化消息队列成功，设置消息队列超时时间为{message_timeout}")

ins_cookies = os.path.join(get_project_path(), "spider", "ins", "ins_cookies.json")
global_log.info(f"ins cookies 路径为{ins_cookies}")

# 账号分流管理
ins_account = [
    {
        "user": r"basharov_aleks",
        "password": r"Provia312AM@@123",
        "code": r"BJ32 NT4C X5O4 6QKS GHBC EBAC D24U 3QRZ",
        "fileDir": r"C:\browser\ins\chrome-basharov_aleks-data",
        "port": 9224
    },
    {
        "user": r"danielkroesche94",
        "password": r"Provia312CH@@123",
        "code": r"IU4X NUVZ E5HJ ZMTL AYYD RWJC 7D63 TGW2",
        "fileDir": r"C:\browser\ins\chrome-danielkroesche94-data",
        "port": 9225
    }
]
