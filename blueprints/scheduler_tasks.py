"""
@ProjectName: DataAnalysis
@FileName：scheduler_tasks.py
@IDE：PyCharm
@Author：Libre
@Time：2024/10/10 上午10:31
"""
from flask import Blueprint

from log.logger import global_log
from spider import run_spider
from spider.sql.data_inner_db import select_video_urls
from spider.template.spider_db_template import CelebrityProfile, InfluencersVideoProjectData

scheduler_task_bp = Blueprint('scheduler_task', __name__)


@scheduler_task_bp.route('/video', methods=['GET'])
def to_update_video_data():
    try:
        res = select_video_urls(InfluencersVideoProjectData.video_url,
                                None,
                                InfluencersVideoProjectData.id)
        for item in res:
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
