"""
@ProjectName: DataAnalysis
@FileName：scheduler_tasks.py
@IDE：PyCharm
@Author：Libre
@Time：2024/10/10 上午10:31
"""
import time

from flask import Blueprint
from sqlalchemy import and_

from log.logger import global_log
from spider import run_spider
from spider.spider_threading import extract_tracking_numbers, threading_logistics
from spider.sql.data_inner_db import select_video_urls
from spider.template.spider_db_template import CelebrityProfile, InfluencersVideoProjectData, \
    logistics_information_sheet
from spider.track.track_spider import run as track_spider

scheduler_task_bp = Blueprint('scheduler_task', __name__)


@scheduler_task_bp.route('/video', methods=['GET'])
def to_update_video_data():
    try:
        res = select_video_urls(InfluencersVideoProjectData.video_url,
                                None,
                                InfluencersVideoProjectData.id)
        global_log.info(f"定时任务 视频信息 -> {res}")
        for item in res:
            if item == "":
                continue
            global_log.info(item)
            run_spider.run_spider(item, {}, 2, "schedule_test")
        return {"status": True, "msg": "success"}
    except Exception as e:
        global_log.error()
        return {"status": False, "msg": str(e)}


@scheduler_task_bp.route('/celebrity', methods=['GET'])
def to_celebrity_video_data():
    try:
        # 任务实现
        res = select_video_urls(CelebrityProfile.index_url,
                                None,
                                CelebrityProfile.id)
        global_log.info(f"定时任务 红人信息 -> {res}")
        for item in res:
            global_log.info(item)
            run_spider.run_spider(item, {}, 1, "schedule_test")
        return {"status": True, "msg": "success"}
    except Exception as e:
        global_log.error()
        return {"status": False, "msg": str(e)}


@scheduler_task_bp.route('/logistics', methods=['GET'])
def to_logistics_data():
    try:
        # 任务实现
        res = select_video_urls(logistics_information_sheet.number,
                                logistics_information_sheet.prior_status != "Delivered",
                                logistics_information_sheet.number)
        trackList = select_video_urls(InfluencersVideoProjectData.trackingNumber,
                                      and_(InfluencersVideoProjectData.trackingNumber != None,
                                           InfluencersVideoProjectData.trackingNumber != "",
                                           InfluencersVideoProjectData.trackingNumber != "test"
                                           ),
                                      InfluencersVideoProjectData.id)
        for track in trackList:
            orderItem = extract_tracking_numbers(track)
            for item in orderItem:
                if item in res:
                    continue
                else:
                    res.append(item)

        #
        global_log.info(f"定时任务 物流信息 -> {res}")
        returnRes = False
        info = None
        for _ in range(5):
            returnRes, info = track_spider(True, res)
            if returnRes:
                break
            else:
                time.sleep(2)

        threading_logistics.set()
        # for item in res:
        #     res = sync_logistics_information_sheet_to_InfluencersVideoProjectData(item)
        #     global_log.info(f"同步情况 {res}")
        return {"status": returnRes, "msg": info}
    except Exception as e:
        global_log.error()
        return {"status": False, "msg": str(e)}


if __name__ == '__main__':
    to_celebrity_video_data()
