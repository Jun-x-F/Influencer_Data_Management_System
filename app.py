from flask import Flask, render_template
from blueprints.influencer import influencer_bp
from blueprints.video import video_bp
from blueprints.update import update_bp
from blueprints.project_information import project_information_bp
from forms import ProjectForm
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 允许所有跨域请求

# 设置 SECRET_KEY
app.config['SECRET_KEY'] = os.urandom(24)

# 日志配置
import logging
from logging.handlers import RotatingFileHandler

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=True)

