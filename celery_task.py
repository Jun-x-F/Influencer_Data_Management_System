"""
@ProjectName: python
@FileName：celery_task.py
@IDE：PyCharm
@Author：Libre
@Time：2024/7/11 下午2:22
"""
import asyncio
import sys

import celery
from celery.schedules import crontab

# 设置事件循环策略
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

backend = "redis://127.0.0.1:6379/0"
broker = "redis://127.0.0.1:6379/1"
cel = celery.Celery('influencer_data_management', broker=broker,
                    backend=backend, include=['spider.spider_threading'])

# 其他 Celery 配置
cel.conf.update(
    broker_connection_retry_on_startup=True,
    timezone='Asia/Shanghai',
    enable_utc=False,
    worker_log_color=True,
    worker_task_log_format="%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s",
    worker_log_format="%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s",
    worker_task_log_datefmt="%Y-%m-%d %H:%M:%S",
    worker_log_datefmt="%Y-%m-%d %H:%M:%S",
    # 定时任务
    beat_schedule={
        'to_celebrity_video_data': {
            'task': 'to_celebrity_video_data',
            'schedule': crontab(day_of_month='15', hour='3', minute='00'),  # 每个月15号 3:00执行一次
        }, 'to_update_video_data': {
            'task': 'to_update_video_data',
            'schedule': crontab(day_of_week='0,1,3,5', hour='0', minute='30')  # 每周1\3\5\7 0点执行
        }
    }
)

# 配置 Celery 使用 LoguruLogger
# celeryLoguruLogger = CeleryLoguruLogger()
# cel.log.setup_logging_subsystem = celeryLoguruLogger.setup_logging
