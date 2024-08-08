# 日志配置
import logging
import os
import threading
import time
from logging.handlers import RotatingFileHandler

from flask import Flask, render_template
from flask_cors import CORS
from flask_socketio import SocketIO

from blueprints.influencer import influencer_bp, submitted_influencer_links
from blueprints.project_information import project_information_bp
from blueprints.update import update_bp
from blueprints.video import video_bp, submitted_video_links
from forms import ProjectForm
from spider import run_spider

app = Flask(__name__)
CORS(app)  # 允许所有跨域请求
app_socketIo = SocketIO(app)

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


@app.route('/')
def index():
    project_form = ProjectForm()
    return render_template('index.html', form=project_form)


def background_task():
    """单独一个线程执行任务"""
    while True:
        # chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\chrome-user-data"
        if submitted_video_links:
            link, platform = submitted_video_links.popitem()
            res = run_spider.run_spider(link, {}, 2)
            print(res)
        if submitted_influencer_links:
            link, platform = submitted_influencer_links.popitem()
            res = run_spider.run_spider(link, {}, 1)
            app_socketIo.emit("process", {"message": "test"})
            print(res)
        time.sleep(1)


if __name__ == '__main__':
    # 在后台启动线程
    thread = threading.Thread(target=background_task, daemon=True)
    thread.start()
    app.run(host='0.0.0.0', port=5000, debug=False)
