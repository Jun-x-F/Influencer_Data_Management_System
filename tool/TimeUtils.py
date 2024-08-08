"""
@ProjectName: DataAnalysis
@FileName：TimeUtils.py
@IDE：PyCharm
@Author：Libre
@Time：2024/8/1 下午4:52
"""

from datetime import datetime, timezone
from typing import Union


class TimeUtils:
    @staticmethod
    def timestamp_to_datetime(timestamp: Union[int, str]) -> datetime:
        """
        将时间戳转换为 datetime 对象

        :param timestamp: 时间戳 (秒级别)
        :return: 转换后的 datetime 对象
        """
        # 将时间戳转换为 datetime 对象，假设时间戳是 UTC 时间
        return datetime.fromtimestamp(int(timestamp), tz=timezone.utc)

    @staticmethod
    def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
        """
        将 datetime 对象格式化为字符串

        :param dt: datetime 对象
        :param format_str: 格式化字符串
        :return: 格式化后的日期时间字符串
        """
        return dt.strftime(format_str)


# 示例用法
if __name__ == "__main__":
    timestamp = 1721852112
    dt = TimeUtils.timestamp_to_datetime(timestamp)
    formatted_time = TimeUtils.format_datetime(dt)

    print(f"时间戳 {timestamp} 转换后的 datetime 对象: {dt}")
    print(f"格式化后的时间: {formatted_time}")
