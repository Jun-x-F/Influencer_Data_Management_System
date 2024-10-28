"""
@ProjectName: DataAnalysis
@FileName：scheduler_tasks.py
@IDE：PyCharm
@Author：Libre
@Time：2024/10/10 上午10:31
"""
import time

from flask import Blueprint

from log.logger import global_log
from spider import run_spider
from spider.sql.data_inner_db import select_video_urls, sync_logistics_information_sheet_to_InfluencersVideoProjectData
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
        print(res)
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

        track_spider(True, res)
        time.sleep(2)
        for item in res:
            res = sync_logistics_information_sheet_to_InfluencersVideoProjectData(item)
            global_log.info(f"同步情况 {res}")
        return {"status": True, "msg": "success"}
    except Exception as e:
        global_log.error()
        return {"status": False, "msg": str(e)}


if __name__ == '__main__':
    to_logistics_data()
