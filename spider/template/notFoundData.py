"""
@ProjectName: Influencer_Data_Management_System
@FileName：notFoundData.py
@IDE：PyCharm
@Author：Libre
@Time：2024/11/15 上午10:04
"""


class NotUserData(Exception):
    """自定义异常类，用于表示非用户数据的错误情况。"""

    def __init__(self, message="数据不符合用户数据的格式或要求。"):
        super().__init__(message)
