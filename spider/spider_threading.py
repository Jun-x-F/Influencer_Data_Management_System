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
from spider.config import config
from spider.config.config import order_links, submitted_influencer_links, submitted_video_links, message_queue
from spider.sql.data_inner_db import sync_logistics_information_sheet_to_InfluencersVideoProjectData
from spider.template.class_dict_template import FIFODict
from spider.track.track_spider import run as track_spider

threading_influencersVideo = threading.Event()


def process_links(_queue: FIFODict, flag: int) -> None:
    """公共代码，执行任务，传入的_queue不是同一个"""
    if not _queue or _queue.is_empty():
        return

    send_id, links = _queue.dequeue()

    # 执行爬虫任务
    message = None
    for link in links:
        message = run_spider.run_spider(link, {}, flag, send_id)

    # 完成通知 如果需要执行物流信息
    if flag == 2 and config.submitted_pass_track is False:
        threading_influencersVideo.set()
    else:
        message_queue.add(send_id, "抓取成功" if message.get("code") == 500 else "抓取失败", status="error" if message.get("code") == 500 else "finish")
        message_queue.to_end(send_id)


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
            message_queue.add(sendId, f"开始执行获取物流信息任务, 接收到{len(order_list)}个订单号")
            res = track_spider(isRequest=True, order_numbers=order_list)
            message_queue.add(sendId, f"任务：获取物流信息结果为{'成功' if res is True else '失败'}，开始执行下一步")
            print(config.submitted_pass_video)
            if config.submitted_pass_video is False:
                threading_influencersVideo.wait(timeout=60 * 2)
            for order in order_list:
                res = sync_logistics_information_sheet_to_InfluencersVideoProjectData(order)
            message_queue.add(sendId, f"抓取任务结果为 {'成功' if res is True else '失败'} ，任务结束", "finish")
            message_queue.to_end(sendId)
        time.sleep(5)


def cleanNoneNotice():
    """删除超时的队列信息"""
    while True:
        expired_list = message_queue.is_expired()
        for expired_item in expired_list:
            message_queue.delete(expired_item)
        time.sleep(10)
