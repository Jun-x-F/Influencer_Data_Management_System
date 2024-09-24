"""
@ProjectName: DataAnalysis
@FileName：TimeUtils.py
@IDE：PyCharm
@Author：Libre
@Time：2024/8/1 下午4:52
"""

from datetime import datetime, timezone
from typing import Union
from zoneinfo import ZoneInfo


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

    @staticmethod
    def convert_time(time_str, target_timezone="Asia/Shanghai"):
        """
        将 UTC 时间字符串转换为指定时区时间。

        参数：
            time_str (str): 时间字符串，格式为 "Sun Sep 22 20:08:19 +0000 2024"
            target_timezone (str): 目标时区名称，默认为 "Asia/Shanghai"

        返回：
            str: 转换后的时间字符串，格式为 "YYYY-MM-DD HH:MM:SS"
            如果转换失败，则返回 None
        """
        try:
            # 定义输入时间格式
            input_format = "%a %b %d %H:%M:%S %z %Y"

            # 解析时间字符串为 datetime 对象
            utc_time = datetime.strptime(time_str, input_format)

            # 转换为目标时区
            china_timezone = ZoneInfo(target_timezone)  # 对于 Python 3.9+
            # china_timezone = pytz.timezone(target_timezone)  # 如果使用 pytz
            target_time = utc_time.astimezone(china_timezone)

            # 格式化输出时间字符串
            output_format = "%Y-%m-%d %H:%M:%S"
            return target_time.strftime(output_format)
        except Exception as e:
            print(f"转换失败: {e}")
            return None


# 示例用法
if __name__ == "__main__":
    timestamp = 1721852112
    dt = TimeUtils.timestamp_to_datetime(timestamp)
    formatted_time = TimeUtils.format_datetime(dt)

    print(f"时间戳 {timestamp} 转换后的 datetime 对象: {dt}")
    print(f"格式化后的时间: {formatted_time}")

    # 示例用法
    if __name__ == "__main__":
        original_time = "Sun Sep 22 20:08:19 +0000 2024"
        target_timezone = "Asia/Shanghai"  # 中国标准时间
        converted_time = TimeUtils.convert_time(original_time, target_timezone)
        if converted_time:
            print(f"原始时间 (UTC): {original_time}")
            print(f"转换后时间 ({target_timezone}): {converted_time}")
        else:
            print("时间转换失败。")
