"""
@ProjectName: DataAnalysis
@FileName：celery_logger_setup.py
@IDE：PyCharm
@Author：Libre
@Time：2024/7/12 上午10:02
"""
from log.logger import LoguruLogger

loguru_logger = LoguruLogger()


class CeleryLoguruLogger:
    def __init__(self):
        self.logger = loguru_logger

    def setup_logging(self, loglevel=None, logfile=None, format=None,
                      colorize=None, hostname=None, **kwargs):
        pass  # Loguru 已经配置完成，这里不需要额外配置

    def get_default_logger(self):
        return self.logger
