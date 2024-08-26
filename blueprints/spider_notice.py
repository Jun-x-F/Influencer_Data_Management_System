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
    global_log.info(f"接收到{search_id}请求消息队列，返回{message_list}")
    return jsonify({
        "status": message_status,
        "message": message_list
    }), 200
