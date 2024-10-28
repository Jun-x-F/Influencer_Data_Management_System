"""
@ProjectName: Influencer_Data_Management_System
@FileName：spider_notice.py
@IDE：PyCharm
@Author：Libre
@Time：2024/8/22 下午1:45
"""
from flask import Blueprint, request, jsonify

from log.logger import global_log
from spider.config.config import message_queue

spider_notice_bp = Blueprint('notice', __name__)


@spider_notice_bp.route('/spider/<string:task_name>', methods=['POST'])
def get_notice_queue(task_name: str):
    response_data = request.json
    response_uid = response_data.get("id")
    search_id = f"{task_name}_{response_uid}"
    message_status = message_queue.is_finished(search_id)
    message_list = message_queue.get(search_id)
    if message_list:
        global_log.info(f"接收到{search_id}请求消息队列，返回{message_list}")
    return jsonify({
        "status": message_status,
        "message": message_list
    }), 200

@spider_notice_bp.route('/api/video_message', methods=['POST'])
def get_video_message():
    response_data = request.json
    uid = response_data.get("uid")
    try:
        message_status = message_queue.is_finished(uid)
        message_list = message_queue.getNew(uid)
        if message_list:
            global_log.info(f"接收到{uid}请求消息队列，返回{message_list}")
        return jsonify({
            "status": message_status,
            "message": message_list
        }), 200
    except Exception as e:
        global_log.error(e)
        return jsonify({
            "status": "wait",
            "message": []
        }), 200

#
# def set_redis_message_queue():
#     while True:
#         allMessage = message_queue.get_all()
#         for uid, value in allMessage.items():
#             # 一小时清除一次
#             cur_message_queue = value.get("message_queue")
#             if cur_message_queue:
#                 redis_conn.set_value(uid, json.dumps(cur_message_queue), 3600)
