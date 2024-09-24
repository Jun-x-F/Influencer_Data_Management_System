@echo off
REM 激活conda环境
call conda activate DataAnalysis_39

REM 启动Celery Worker
start "Celery Worker" cmd /k "conda activate DataAnalysis_39 && celery -A celery_task worker --loglevel=info --pool=threads --concurrency=4"

REM 启动Celery Beat
start "Celery Beat" cmd /k "conda activate DataAnalysis_39 && celery -A celery_task beat --loglevel=info"
