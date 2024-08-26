"""
@ProjectName: Influencer_Data_Management_System
@FileName：spider_notice.py
@IDE：PyCharm
@Author：Libre
@Time：2024/8/9 上午9:44
"""
import time


class Message:
    """生成消息对象，方便后续开发使用"""
    def __init__(self, uid, message):
        self.__uid = uid
        self.__message = message
        self.__timestamp = int(time.time())
        self.__status = "create"

    @property
    def uid(self):
        """不可修改"""
        return self.__uid

    @property
    def timestamp(self):
        """不可修改"""
        return self.__timestamp

    @property
    def message(self):
        """不可修改"""
        return self.__message

    @property
    def status(self):
        """不可修改"""
        return self.__status

    def set_status(self, status):
        """create, finish, expired"""
        self.__status = status

    def __eq__(self, __value):
        """判断是否存在"""
        """"1" == a 实际上匹配的是 1 == self.uid"""
        return __value == self.uid

    def __repr__(self):
        return (f"{self.__class__.__name__}(uid=`{self.uid}`, message=`{self.message}`, timestamp={self.timestamp}, "
                f"status=`{self.status}`)")


if __name__ == '__main__':
    a = Message("1", "test")
    print(a)
    print(a.get_status())
    print("1" == a)
    print(a.message)
