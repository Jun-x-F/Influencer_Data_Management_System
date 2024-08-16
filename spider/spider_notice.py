"""
@ProjectName: Influencer_Data_Management_System
@FileName：spider_notice.py
@IDE：PyCharm
@Author：Libre
@Time：2024/8/9 上午9:44
"""
from datetime import datetime, timedelta
from queue import Queue
from typing import Optional

from flask import Blueprint, request, jsonify

from blueprints.influencer import submitted_influencer_links
from log.logger import global_log

spider_notice_bp = Blueprint('notice', __name__)


class Notice:
    def __init__(self):
        # 生成存储
        self.notice_info = {}
        self.work_id_time = {}
        self.del_id_info = {}
        self.use_id = None

    def to_notice(self, _id: str) -> Optional[str]:
        """获取队列里面的数据"""
        message_queue: Optional[Queue] = self.notice_info.get(_id, None)
        if message_queue is None:
            # 如果message_queue为None，则说明没有这个值，则认定为被clean或还没有获取到
            return self.del_id_info.get(_id)
        if not message_queue.empty():
            return message_queue.get()
        return None

    def clean_id_notice(self, _id: str) -> None:
        """删除指定id的notice"""
        del self.notice_info[_id]
        del self.work_id_time[_id]
        self.del_id_info[_id] = "clean"

    def add_notice(self, _id: str, message: str) -> None:
        """添加队列消息"""
        message_queue = self.notice_info.get(_id, Queue())
        message_queue.put(message)
        self.notice_info[_id] = message_queue
        # 根据每一次队列写入数据避免异常数据过多
        work_info = self.work_id_time.get(_id, {})
        work_info["更新时间"] = datetime.now()
        self.work_id_time[_id] = work_info

    def finish_notice(self, _id: str) -> None:
        """更新成功"""
        work_info = self.work_id_time[_id]
        work_info["isSuccess"] = True
        self.work_id_time[_id] = work_info

    def get_finish_notice(self, _id: str) -> bool and str:
        """获取是否成功的通知"""
        last_message = ""
        work_info = self.work_id_time.get(_id)
        if work_info is None:
            return False, last_message
        isSuccess = work_info.get("isSuccess", False)
        if isSuccess is True:
            while True:
                # 最后一次将所有数据统一返回
                cur = self.to_notice(_id)
                if cur is None:
                    break
                last_message += cur + "\n"
            self.clean_id_notice(_id)
        return isSuccess, last_message

    def clean_none_notice(self) -> None:
        """清除掉没有人使用的id"""
        for _id, work_info in self.work_id_time.items():
            updateTime = work_info.get("更新时间")
            time_diff = datetime.now() - updateTime
            if time_diff > timedelta(hours=1):
                global_log.info(f"清除 send_id:{_id}")
                self.clean_id_notice(_id)


@spider_notice_bp.route('/spider/celebrity', methods=['POST'])
def post_spider_notice_to_celebrity():
    request_data = request.json
    return_id = request_data.get("id")
    isSuccess, last_message = spider_notice_to_celebrity.get_finish_notice(return_id)
    if isSuccess:
        return jsonify({"message": last_message, "isSuccess": isSuccess, "status": "finish"}), 200
    return_message = spider_notice_to_celebrity.to_notice(return_id)
    if return_id != spider_notice_to_celebrity.use_id:
        return jsonify(
            {"message": f"排队处理中...队列目前有{submitted_influencer_links.total_size()}个请求", "isSuccess": False,
             "status": "wait"}), 200
    if return_message is None:
        return jsonify({"message": "wait working", "status": "wait"}), 200
    if return_message == "clean":
        return jsonify({"message": "clean", "status": "clean"}), 200
    return jsonify({"message": return_message, "status": "doing"}), 200


@spider_notice_bp.route('/spider/influencersVideo', methods=['POST'])
def post_spider_notice_to_influencersVideo():
    request_data = request.json
    return_id = request_data.get("id")
    isSuccess, last_message = spider_notice_to_influencersVideo.get_finish_notice(return_id)
    if isSuccess:
        return jsonify({"message": last_message, "isSuccess": isSuccess, "status": "finish"}), 200
    return_message = spider_notice_to_influencersVideo.to_notice(return_id)
    if return_id != spider_notice_to_influencersVideo.use_id:
        return jsonify(
            {"message": f"排队处理中...队列目前有{submitted_influencer_links.total_size()}个请求", "isSuccess": False,
             "status": "wait"}), 200
    if return_message is None:
        return jsonify({"message": "wait working", "status": "wait"}), 200
    if return_message == "clean":
        return jsonify({"message": "clean", "status": "clean"}), 200
    return jsonify({"message": return_message, "status": "doing"}), 200


# 全局化
spider_notice_to_celebrity = Notice()
spider_notice_to_influencersVideo = Notice()
