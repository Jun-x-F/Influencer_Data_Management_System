"""
@ProjectName: Influencer_Data_Management_System
@FileName：spider_threading.py
@IDE：PyCharm
@Author：Libre
@Time：2024/8/16 下午5:44
"""
import re
import threading
import time
from collections import deque

from log.logger import global_log
from spider import run_spider
from spider.config.config import order_links, submitted_influencer_links, submitted_video_links, message_queue
from spider.sql.data_inner_db import sync_logistics_information_sheet_to_InfluencersVideoProjectData
from spider.template.class_dict_template import FIFODict
from spider.track.track_spider import run as track_spider

threading_influencersVideo = threading.Event()


def extract_tracking_numbers(text):
    # Regular expression pattern to match tracking numbers like UJ712686735YP
    pattern = r'[A-Z]{2}\d{9}[A-Z]{2}'
    # Find all occurrences of the pattern in the text
    tracking_numbers = re.findall(pattern, text)
    return tracking_numbers


def process_links(_queue: FIFODict, flag: int) -> None:
    """
    公共代码，执行任务，传入的_queue不是同一个
    可能存在有物流订单但是没有视频链接的问题，需要进行判断
    优先缓存3秒，保证流程执行完毕之后才进行其他操作
    """
    # 忙等待
    time.sleep(2)
    send_id = None
    message = None
    error_links_list = []
    success_links_list = []
    success_order_list = []
    error_order_list = []

    # 红人
    if flag == 1:
        if not _queue or _queue.is_empty():
            return
        send_id, links = _queue.dequeue()
        for link in links:
            message = run_spider.run_spider(link, {}, flag, send_id)
            if message.get("code") == 500:
                error_links_list.append(link)
            elif message.get("code") == 200:
                success_links_list.append(link)
    # 视频
    elif flag == 2:
        if _queue.is_empty() and order_links.is_empty():
            return

        if not _queue.is_empty() and _queue:
            send_id, links = _queue.dequeue()

            for link in links:
                message = run_spider.run_spider(link, {}, flag, send_id)
                if message.get("code") == 500:
                    error_links_list.append(link)
                elif message.get("code") == 200:
                    success_links_list.append(link)

            if len(error_links_list) > 0:
                message_queue.add(send_id, f"执行失败链接: {error_links_list}", "error")
            else:
                message_queue.add(send_id, f"获取视频信息结果 成功")

    if send_id is not None:
        order_links_deque: deque = order_links.pop(send_id)
    else:
        send_id, order_links_deque = order_links.dequeue()

    if order_links_deque is not None:
        for order_link in order_links_deque:
            order_ls = extract_tracking_numbers(order_link)
            global_log.info(f"提取出来订单信息为{order_ls}, 开始执行")
            message_queue.add(send_id, f"开始获取物流信息，订单列表为 {order_ls}")
            res = False
            res_message = None
            for _ in range(3):
                res, res_message = track_spider(isRequest=True, order_numbers=order_ls)
                if res is True:
                    break
                message_queue.add(send_id, f"重试获取物流信息，原因：网络问题...")
                time.sleep(3)
            message_queue.add(send_id, f"获取物流信息结果为{'成功' if res is True else res_message}...")
            if res is False:
                error_order_list.append(order_link)
                global_log.info("任务: 同步物流信息跳过, 原因获取物流信息报错...")
            else:
                success_order_list.append(order_link)
                for order in order_ls:
                    res = sync_logistics_information_sheet_to_InfluencersVideoProjectData(order)
                    global_log.info(f"任务：同步物流信息 -> {res}")

    if len(error_links_list) > 0:
        message_queue.add(send_id, f"以下链接都失败了\n{error_links_list}", status="error")
    elif len(error_order_list) > 0:
        message_queue.add(send_id, f"以下物流链接都失败了\n{error_order_list}", status="error")
    else:
        message_queue.add(send_id, "成功", status="finish")
    # message_queue.to_end(send_id)
    global_log.info(f"本次执行结果: \n成功链接共有\n{success_links_list}\n成功物流链接共有\n{success_order_list}\n失败链接共有\n{error_links_list}\n失败物流链接共有\n{error_order_list}")


def process_video_links():
    while True:
        process_links(submitted_video_links, 2)
        time.sleep(5)


def process_influencer_links():
    while True:
        process_links(submitted_influencer_links, 1)
        time.sleep(5)


# def background_task():
#     """单独一个线程执行任务"""
#     while True:
#         # chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\chrome-user-data"
#         process_links(submitted_video_links, 2)
#         process_links(submitted_influencer_links, 1)
#         time.sleep(5)

def cleanNoneNotice():
    """删除超时的队列信息"""
    while True:
        expired_list = message_queue.is_expired()
        for expired_item in expired_list:
            message_queue.delete(expired_item)
        time.sleep(10)
