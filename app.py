# 日志配置
import logging
import os
import threading
import time
from logging.handlers import RotatingFileHandler

from flask import Flask, render_template
from flask_cors import CORS

from blueprints.get_file import image_bp
from blueprints.influencer import influencer_bp, submitted_influencer_links
from blueprints.project_information import project_information_bp
from blueprints.update import update_bp
from blueprints.video import video_bp, submitted_video_links
from forms import ProjectForm
from spider import run_spider
from spider.spider_notice import spider_notice, spider_notice_bp
from spider.template.class_dict_template import FIFODict

app = Flask(__name__)
CORS(app)  # 允许所有跨域请求

# 设置 SECRET_KEY
app.config['SECRET_KEY'] = os.urandom(24)

handler = RotatingFileHandler('app.log', maxBytes=100000, backupCount=10)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)

# 注册蓝图
app.register_blueprint(influencer_bp, url_prefix='/influencer')
app.register_blueprint(video_bp, url_prefix='/video')
app.register_blueprint(update_bp, url_prefix='/update')
app.register_blueprint(project_information_bp, url_prefix='/project_information')
app.register_blueprint(spider_notice_bp, url_prefix='/notice')
app.register_blueprint(image_bp, url_prefix='/image')

@app.route('/')
def index():
    project_form = ProjectForm()
    return render_template('index.html', form=project_form)


def process_links(_queue: FIFODict, flag: int) -> None:
    """公共代码，执行任务，传入的_queue不是同一个"""
    if _queue:
        send_id, links = _queue.dequeue()
        spider_notice.use_id = send_id
        for link in links:
            run_spider.run_spider(link, {}, flag, send_id)
        spider_notice.finish_notice(send_id)


def background_task():
    """单独一个线程执行任务"""
    while True:
        # chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\chrome-user-data"
        process_links(submitted_video_links, 2)
        process_links(submitted_influencer_links, 1)
        time.sleep(1)


def cleanNoneNotice():
    while True:
        spider_notice.clean_none_notice()
        time.sleep(10)


if __name__ == '__main__':
    # 在后台启动线程
    thread_background_task = threading.Thread(target=background_task, daemon=True)
    thread_cleanNoneNotice = threading.Thread(target=cleanNoneNotice, daemon=True)
    thread_background_task.start()
    thread_cleanNoneNotice.start()
    app.run(host='0.0.0.0', port=5000, debug=True)
