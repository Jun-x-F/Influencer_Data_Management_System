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

# 设置事件循环策略
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

backend = "redis://default:My$trongP@ssw0rd123!@172.16.11.167:6379/0"
broker = "redis://default:My$trongP@ssw0rd123!@172.16.11.167:6379/1"
cel = celery.Celery('Influencer_Data_Management_System', broker=broker, backend=backend, include=['tasks'])

# 其他 Celery 配置
cel.conf.update(
    task_default_queue='Influencer_Data_Management_System',
    broker_connection_retry_on_startup=True,
    timezone='Asia/Shanghai',
    enable_utc=False,
    worker_log_color=True,
    worker_task_log_format="%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s",
    worker_log_format="%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s",
    worker_task_log_datefmt="%Y-%m-%d %H:%M:%S",
    worker_log_datefmt="%Y-%m-%d %H:%M:%S"
)

