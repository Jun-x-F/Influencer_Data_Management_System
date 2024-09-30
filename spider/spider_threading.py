"""
@ProjectName: Influencer_Data_Management_System
@FileName：spider_threading.py
@IDE：PyCharm
@Author：Libre
@Time：2024/8/16 下午5:44
"""
import threading
import time

from celery_task import cel
from spider import run_spider
from spider.config import config
from spider.config.config import order_links, submitted_influencer_links, submitted_video_links, message_queue
from spider.sql.data_inner_db import sync_logistics_information_sheet_to_InfluencersVideoProjectData, select_video_urls
from spider.template.class_dict_template import FIFODict
from spider.template.spider_db_template import InfluencersVideoProjectData, CelebrityProfile
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
        message_queue.add(send_id, message.get("message"),
                          status="error" if message.get("code") == 500 else "doing")
        threading_influencersVideo.set()
    else:
        message_queue.add(send_id, "成功" if message.get("code") == 200 else message.get("message"),
                          status="error" if message.get("code") == 500 else "finish")
        message_queue.to_end(send_id)


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


def getTrackInfo():
    while True:
        if order_links:
            sendId, order_list = order_links.dequeue()
            message_queue.add(sendId, f"开始执行获取物流信息任务, 接收到{len(order_list)}个订单号")
            res, res_message = track_spider(isRequest=True, order_numbers=order_list)
            message_queue.add(sendId, f"获取物流信息结果为{'成功' if res is True else res_message}...",
                              "finish" if res is True else "error")
            message_queue.to_end(sendId)
            print(config.submitted_pass_video)
            if config.submitted_pass_video is False:
                threading_influencersVideo.wait(timeout=60 * 2)
            if res is False:
                continue
            for order in order_list:
                res = sync_logistics_information_sheet_to_InfluencersVideoProjectData(order)
                print("同步物流信息", res)
        time.sleep(5)


def cleanNoneNotice():
    """删除超时的队列信息"""
    while True:
        expired_list = message_queue.is_expired()
        for expired_item in expired_list:
            message_queue.delete(expired_item)
        time.sleep(10)


@cel.task(name="to_update_video_data")
def to_update_video_data():
    # res = select_video_urls(InfluencersVideoProjectData.video_url,
    #                         InfluencersVideoProjectData.progressCooperation.notlike(f"合作完成"))
    res = select_video_urls(InfluencersVideoProjectData.video_url,
                            InfluencersVideoProjectData.full_name == None,
                            InfluencersVideoProjectData.id)
    print(res)
    for item in res:
        print(item)
        run_spider.run_spider(item, {}, 2, "schedule_test")


@cel.task(name="to_celebrity_video_data")
def to_celebrity_video_data():
    res = select_video_urls(CelebrityProfile.index_url,
                            None,
                            CelebrityProfile.id)
    for item in res:
        run_spider.run_spider(item, {}, 1, "schedule_test")


# # 每周一、周三、周五、周日执行任务
# schedule.every().monday.at("02:00").do(to_update_video_data)
# schedule.every().wednesday.at("02:00").do(to_update_video_data)
# schedule.every().friday.at("02:00").do(to_update_video_data)
# schedule.every().sunday.at("02:00").do(to_update_video_data)
#
# # 每14天执行一次
# schedule.every(14).days.at("02:00").do(to_celebrity_video_data)
#
#
# def update_video_times():
#     """每2天更新一次视频数据"""
#     while True:
#         schedule.run_pending()
#         time.sleep(1)

if __name__ == '__main__':
    to_update_video_data()
