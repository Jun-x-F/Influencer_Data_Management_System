# 日志配置
import logging
import os
import threading

from flask import Flask, render_template
from flask_cors import CORS

from blueprints.get_file import image_bp
from blueprints.influencer import influencer_bp
from blueprints.project_information import project_information_bp
from blueprints.update import update_bp
from blueprints.video import video_bp
from forms import ProjectForm
from log.logger import InterceptHandler
from spider.spider_notice import spider_notice_bp
from spider.spider_threading import getTrackInfo, cleanNoneNotice, background_task

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


@app.route('/')
def index():
    project_form = ProjectForm()
    return render_template('index.html', form=project_form)


if __name__ == '__main__':
    # 在后台启动线程
    thread_background_task = threading.Thread(target=background_task, daemon=True)
    thread_cleanNoneNotice = threading.Thread(target=cleanNoneNotice, daemon=True)
    thread_getTrackInfo = threading.Thread(target=getTrackInfo, daemon=True)
    thread_background_task.start()
    thread_cleanNoneNotice.start()
    thread_getTrackInfo.start()
    app.run(host='0.0.0.0', port=5000, debug=False)
