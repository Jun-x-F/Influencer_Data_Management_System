import re
from collections import deque

from flask import Blueprint, request, jsonify

from base import ReadDatabase
from spider.template.class_dict_template import FIFODict
from utils import determine_platform

influencer_bp = Blueprint('influencer', __name__)

# 用于存储用户提交的红人链接
submitted_influencer_links = FIFODict()


class Influencer:
    @staticmethod
    @influencer_bp.route('/submit_link', methods=['POST'])
    def submit_link():
        try:
            data = request.json
            link = data.get('link')
            send_id = data.get('id')

            # Validate input
            if not link:
                return jsonify({'message': '链接是必需的。'}), 400

            # Validate URL format
            url_pattern = re.compile(r'^(http|https)://')
            if not url_pattern.match(link):
                return jsonify({'message': '无效的URL格式。'}), 400

            # Determine platform based on URL
            platform = determine_platform(link)
            if not platform:
                return jsonify({'message': '不支持的平台。'}), 400

            # Add link to submitted_influencer_links
            send_id_links: deque = submitted_influencer_links.get(send_id, deque())
            if link in send_id_links:
                return jsonify({'message': f'链接{link} 存在队列中, 请勿重复生成任务'}), 200
            send_id_links.append(link)
            submitted_influencer_links[send_id] = send_id_links

            # Simulate data fetching
            # message = f'{platform.capitalize()}的红人链接提交成功。\n数据抓取中...'
            # message += '\n数据抓取成功。\n存储数据中...'
            # message += '\n数据存储成功。'
            message = ""
            # while True:
            #     if notice_flag is True:
            #         for i in range(spider_notice.qsize()):
            #             message += f"{spider_notice.get()} \n"
            #         break
            # spider.run_spider.notice_flag = False
            return jsonify({'message': message}), 200

        except Exception as e:
            print(f"Error: {e}")
            return jsonify({'message': '内部服务器错误。'}), 500

    @staticmethod
    @influencer_bp.route('/get_influencer_data', methods=['GET'])
    def get_influencer_data():
        DATABASE = 'marketing'
        sql_t = 'celebrity_profile'
        try:
            data = ReadDatabase(DATABASE, f'SELECT * FROM {sql_t}').vm()  # 假设 ReadDatabase 函数返回的是 DataFrame
            data = data.replace({float('nan'): None, float('inf'): None, float('-inf'): None})
            result = data.to_dict(orient='records')  # 将 DataFrame 转换为字典列表
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
