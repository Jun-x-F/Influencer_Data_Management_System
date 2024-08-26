"""
@ProjectName: Influencer_Data_Management_System
@FileName：spider_notice.py
@IDE：PyCharm
@Author：Libre
@Time：2024/8/9 上午9:44
"""
import threading
import time
from queue import Queue
from typing import Optional

from spider.template.class_message_template import Message


class Notice:
    """线程安全的消息队列"""

    def __init__(self, message_time_out):
        # 为了保证线程安全
        self.lock = threading.Lock()
        # 新增检索功能
        self.__message_dict = {}
        self.__message_time_out = message_time_out

    @property
    def info(self):
        return self.__message_dict

    def add(self, uid, message, status=None):
        """添加消息对象到队列中，自更新时间"""
        with self.lock:
            message_info = self.__message_dict.get(uid, {})
            message_queue = message_info.get("message_queue", Queue())
            message_info["message_queue"] = message_queue
            _cur = Message(uid, message)
            if status is not None:
                _cur.set_status(status)
            message_queue.put(_cur)
            # message_info["isSuccess"] = status == "finish" or status == "error"
            message_info["status"] = "doing"
            message_info["update_time"] = int(time.time())
            self.__message_dict[uid] = message_info

    def to_end(self, uid):
        with self.lock:
            message_info = self.__message_dict.get(uid)
            message_queue: Queue = message_info.get("message_queue")
            for last_message in list(message_queue.queue):
                info = last_message.status
                if info == "finish" or info == "error":
                    message_info["status"] = last_message.status
                    break
            self.__message_dict[uid] = message_info

    def get(self, uid) -> list:
        """获取同一个uid下面的所有消息"""
        cur = []
        with self.lock:
            message_info: Optional[dict] = self.__message_dict.get(uid, None)
            if message_info is None:
                return cur
            message_queue: Optional[Queue] = message_info.get("message_queue")
            if message_queue is None:
                return cur

            while not message_queue.empty():
                cur_message: Message = message_queue.get()
                cur.append({
                    "message": cur_message.message,
                    "status": cur_message.status
                })
            message_info["message_queue"] = message_queue
            self.__message_dict[uid] = message_info
        return cur

    def delete(self, uid):
        """根据uid进行删除整个dict"""
        with self.lock:
            _cur = self.__message_dict.get(uid)
            if _cur is not None:
                del self.__message_dict[uid]

    def is_expired(self) -> list:
        """返回超时队列uid"""
        cur = []
        with self.lock:
            cur_time = int(time.time())
            for uid, message_info in self.__message_dict.items():
                update_time = message_info.get("update_time")
                ex = cur_time - update_time
                if ex > self.__message_time_out:
                    cur.append(uid)
        return cur

    def is_finished(self, uid) -> Optional[str]:
        """判断是否完成"""
        _cur = self.__message_dict.get(uid)
        if _cur is None:
            return "wait"
        return _cur["status"]

    def __repr__(self):
        # 构造包含队列内容的字典表示
        display_dict = {}
        for uid, info in self.__message_dict.items():
            queue_contents = list(info["message_queue"].queue)  # 复制队列内容到列表中
            display_dict[uid] = {
                "message_queue": queue_contents,
                "update_time": info["update_time"],
                "status": info["status"]
            }
        return f"{display_dict}"


if __name__ == '__main__':
    test_notice_queue = Notice(5 * 60)
    test_notice_queue.add("test", "test")
    test_notice_queue.add("test2", "test")
    test_notice_queue.add("test2", "test")
    test_notice_queue.add("test3", "test")
    test_notice_queue.add("test3", "test", "finish")
    print(test_notice_queue.get("test3"))
    print(test_notice_queue)
    print(test_notice_queue.is_finished("test3"))
