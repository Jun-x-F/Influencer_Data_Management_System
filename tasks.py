"""
@ProjectName: DataAnalysis
@FileName：tasks.py
@IDE：PyCharm
@Author：Libre
@Time：2024/10/10 上午10:31
"""

from celery_task import cel
from log.logger import global_log
from spider import run_spider
from spider.sql.data_inner_db import select_video_urls
from spider.template.spider_db_template import CelebrityProfile, InfluencersVideoProjectData


@cel.task(name='to_update_video_data')
def to_update_video_data():
    res = select_video_urls(InfluencersVideoProjectData.video_url,
                            None,
                            InfluencersVideoProjectData.id)
    for item in res:
        global_log.info(item)
        run_spider.run_spider(item, {}, 2, "schedule_test")


@cel.task(name='to_celebrity_video_data')
def to_celebrity_video_data():
    # 任务实现
    res = select_video_urls(CelebrityProfile.index_url,
                            None,
                            CelebrityProfile.id)
    for item in res:
        global_log.info(item)
        run_spider.run_spider(item, {}, 1, "schedule_test")


