"""
@ProjectName: DataAnalysis
@FileName：microsofttranslator.py
@IDE：PyCharm
@Author：Libre
@Time：2024/8/16 上午9:52
"""
import time

import requests

from log.logger import global_log
from spider.template.proxy_template import proxy

auth_config = {
}


def is_within_8_minutes(timestamp):
    # 获取当前时间的时间戳（秒）
    current_time = time.time()

    # 计算两个时间戳之间的差值，单位是秒
    time_difference = current_time - timestamp

    # 将8分钟转换为秒（8分钟 = 8 * 60秒）
    eight_minutes_in_seconds = 8 * 60

    # 判断时间差是否小于等于8分钟
    return time_difference <= eight_minutes_in_seconds


def get_auth():
    auth = requests.get("https://edge.microsoft.com/translate/auth", proxies=proxy).text
    global_log.info(f"请求翻译auth认证长度: {len(auth)}")
    return auth


def translate(text):
    if auth_config == {}:
        auth_config["auth"] = get_auth()
        auth_config["saveTime"] = time.time()
    else:
        saveTime = auth_config.get("saveTime")
        res = is_within_8_minutes(saveTime)
        if res is False:
            auth_config["auth"] = get_auth()
            auth_config["saveTime"] = time.time()

    headers = {
        "accept": "*/*",
        "accept-language": "zh-CN,zh;q=0.9",
        "authorization": f"Bearer {auth_config.get('auth')}",
        "cache-control": "no-cache",
        "content-type": "application/json; charset=UTF-8",
        "origin": "https://t.17track.net",
        "pragma": "no-cache",
        "priority": "u=1, i",
        "referer": "https://t.17track.net/",
        "sec-ch-ua": "\"Not)A;Brand\";v=\"99\", \"Google Chrome\";v=\"127\", \"Chromium\";v=\"127\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
    }
    url = "https://api-edge.cognitive.microsofttranslator.com/translate"
    params = {
        "api-version": "3.0",
        "to": "zh-Hans",
        "includeSentenceLength": "true"
    }
    data = text.encode('unicode_escape')
    response = requests.post(url, headers=headers, params=params, data=data, proxies=proxy)
    global_log.info(f"请求翻译接口结果为: {response.status_code}")
    return response.json()


if __name__ == '__main__':
    print(translate('[{"text":"italia"}]'))
