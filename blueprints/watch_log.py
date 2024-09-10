"""
@ProjectName: Influencer_Data_Management_System
@FileName：watch_log.py
@IDE：PyCharm
@Author：Libre
@Time：2024/9/6 上午9:55
"""
import os

from flask import Blueprint, request, jsonify

from tool.FileUtils import get_project_path

log_bp = Blueprint('log', __name__)


@log_bp.route("", methods=['GET', 'POST'])
def update_log():
    try:
        info = request.args.get("name")
        level = request.args.get("level")
        fetch_data = []
        log_path = os.path.join(get_project_path(), "app.log")
        with open(log_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                if info is not None and level is not None:
                    if info in line and level.upper() in line:
                        fetch_data.append(line)
                elif level is not None:
                    if level.upper() in line:
                        fetch_data.append(line)
                elif info is not None:
                    if info in line:
                        fetch_data.append(line)
                else:
                    fetch_data.append(line)
        return jsonify(fetch_data), 200
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500
