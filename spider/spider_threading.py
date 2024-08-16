"""
@ProjectName: Influencer_Data_Management_System
@FileName：spider_threading.py
@IDE：PyCharm
@Author：Libre
@Time：2024/8/16 下午5:44
"""
import threading
import time

from spider import run_spider
from spider.config.config import order_links, submitted_influencer_links, submitted_video_links
from spider.spider_notice import spider_notice_to_influencersVideo, spider_notice_to_celebrity
from spider.sql.data_inner_db import sync_logistics_information_sheet_to_InfluencersVideoProjectData
from spider.template.class_dict_template import FIFODict
from spider.track.track_spider import run as track_spider

threading_influencersVideo = threading.Event()


def process_links(_queue: FIFODict, flag: int) -> None:
    """公共代码，执行任务，传入的_queue不是同一个"""
    if not _queue or _queue.is_empty():
        return

    send_id, links = _queue.dequeue()

    # 选择合适地处理对象
    notice_handler = (spider_notice_to_celebrity
                      if flag == 1
                      else spider_notice_to_influencersVideo)

    # 设置使用的ID
    notice_handler.use_id = send_id

    # 执行爬虫任务
    for link in links:
        run_spider.run_spider(link, {}, flag, send_id)

    # 完成通知
    if flag == 2:
        threading_influencersVideo.set()
    notice_handler.finish_notice(send_id)


def background_task():
    """单独一个线程执行任务"""
    while True:
        # chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\chrome-user-data"
        process_links(submitted_video_links, 2)
        process_links(submitted_influencer_links, 1)
        time.sleep(5)


def getTrackInfo():
    while True:
        if order_links:
            sendId, order_list = order_links.dequeue()
            spider_notice_to_influencersVideo.add_notice(sendId,
                                                         f"开始获取物流信息, 接收到{len(order_list)}个订单号")
            res = track_spider(isRequest=True, order_numbers=order_list)
            spider_notice_to_influencersVideo.add_notice(sendId,
                                                         f"获取物流信息结果为{res}，正在同步表格数据")
            # 等待2秒
            time.sleep(2)
            for order in order_list:
                sync_logistics_information_sheet_to_InfluencersVideoProjectData(order)
            threading_influencersVideo.wait(timeout=60 * 2)
            spider_notice_to_influencersVideo.add_notice(sendId, "执行完毕")
            spider_notice_to_influencersVideo.finish_notice(sendId)
        time.sleep(5)


def cleanNoneNotice():
    while True:
        spider_notice_to_celebrity.clean_none_notice()
        spider_notice_to_influencersVideo.clean_none_notice()
        time.sleep(10)
