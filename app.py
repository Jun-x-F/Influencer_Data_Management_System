from flask import Flask, request, jsonify, render_template
import re

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/submit_influencer_link', methods=['POST'])
def submit_influencer_link():
    try:
        data = request.json
        link = data.get('link')

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

        # Print the link and platform
        print(f"红人链接: {link}, 平台: {platform}")

        # Simulate data fetching
        message = f'{platform.capitalize()}的红人链接提交成功。\n数据抓取中...'
        print(message)

        # Simulate data fetched
        message += '\n数据抓取成功。\n存储数据中...'
        print(message)

        # Simulate data stored
        message += '\n数据存储成功。'
        print(message)

        return jsonify({'message': message}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'message': '内部服务器错误。'}), 500


@app.route('/submit_video_link', methods=['POST'])
def submit_video_link():
    try:
        data = request.json
        link = data.get('link')

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

        # Print the link and platform
        print(f"视频链接: {link}, 平台: {platform}")

        # Simulate data fetching
        message = f'{platform.capitalize()}的视频链接提交成功。\n数据抓取中...'
        print(message)

        # Simulate data fetched
        message += '\n数据抓取成功。\n存储数据中...'
        print(message)

        # Simulate data stored
        message += '\n数据存储成功。'
        print(message)

        return jsonify({'message': message}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'message': '内部服务器错误。'}), 500


def determine_platform(link):
    if 'youtube.com' in link or 'youtu.be' in link:
        return 'youtube'
    elif 'instagram.com' in link:
        return 'instagram'
    elif 'tiktok.com' in link:
        return 'tiktok'
    else:
        return None


if __name__ == '__main__':
    app.run(debug=True)
