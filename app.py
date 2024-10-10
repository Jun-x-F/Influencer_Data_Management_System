# 日志配置
import logging
import os
import threading
import time

from flask import Flask, render_template, redirect, url_for, request
from flask_cors import CORS

from blueprints.get_file import image_bp
from blueprints.influencer import influencer_bp
from blueprints.project_information import project_information_bp
from blueprints.spider_notice import spider_notice_bp
from blueprints.update import update_bp
from blueprints.video import video_bp
from blueprints.watch_log import log_bp
from log.logger import InterceptHandler
# from spider.spider_notice import spider_notice_bp
from spider.spider_threading import cleanNoneNotice, \
    process_influencer_links, process_video_links

app = Flask(__name__)
CORS(app)  # 允许所有跨域请求

# 设置 SECRET_KEY
app.config['SECRET_KEY'] = os.urandom(24)

# 移除 Flask 默认的日志处理器
for handler in list(app.logger.handlers):
    app.logger.removeHandler(handler)
# 移除 Werkzeug 默认的日志处理器
logging.getLogger('werkzeug').handlers = []
# 设置全局日志配置，将所有日志重定向到 Loguru
logging.basicConfig(handlers=[InterceptHandler()], level=logging.INFO)

# 注册蓝图
app.register_blueprint(influencer_bp, url_prefix='/influencer')
app.register_blueprint(video_bp, url_prefix='/video')
app.register_blueprint(update_bp, url_prefix='/update')
app.register_blueprint(project_information_bp, url_prefix='/project_information')
app.register_blueprint(spider_notice_bp, url_prefix='/notice')
app.register_blueprint(image_bp, url_prefix='/image')
app.register_blueprint(log_bp, url_prefix='/log')


@app.after_request
def add_header(response):
    """
    根据请求路径设置不同的缓存策略。
    """
    if 'image' not in request.path:
        # 对于其他路径，设置为不缓存
        response.cache_control.no_store = True
        response.cache_control.no_cache = True
        response.cache_control.must_revalidate = True
        response.headers['Expires'] = '0'
        response.headers['Pragma'] = 'no-cache'
    return response


@app.route('/')
def root():
    # 重定向到红人页面
    return redirect(url_for('influencers_page'))


@app.route('/influencers')
def influencers_page():
    return render_template('influencers.html', version=int(time.time()))


@app.route('/videos')
def videos_page():
    return render_template('videos.html', version=int(time.time()))


def start_thread(target):
    """辅助函数用于创建和启动线程"""
    thread = threading.Thread(target=target, daemon=True)
    thread.start()
    return thread


if __name__ == '__main__':
    # 在后台启动线程
    # 启动所有线程
    threads = [
        start_thread(process_influencer_links),
        start_thread(process_video_links),
        start_thread(cleanNoneNotice),
    ]
    app.run(host='0.0.0.0', port=5000, debug=False)
