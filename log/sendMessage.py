"""
@ProjectName: Influencer_Data_Management_System
@FileName：sendMessage.py
@IDE：PyCharm
@Author：Libre
@Time：2024/11/6 上午10:12
"""
import base64
import hashlib
import hmac
import json
import time
from urllib.parse import quote_plus

import requests


def sendMessage(title, info):
    """
    @FunctionName：_send_dingtalk(self, content):
    @Description：钉钉提醒, 缺失IP
    @Author：Libre
    @Return:
    @CreateDate: 2023/7/18
    """
    timestamp = str(round(time.time() * 1000))
    secret = "SEC924fe0a18efd73311e7b51385f6b9404c0badac726f386ec03a8f3c75903d05b"
    secret_enc = secret.encode("utf-8")
    string_to_sign = "{}\n{}".format(timestamp, secret)
    string_to_sign_enc = string_to_sign.encode("utf-8")
    hmac_code = hmac.new(
        secret_enc, string_to_sign_enc, digestmod=hashlib.sha256
    ).digest()
    sign = quote_plus(base64.b64encode(hmac_code))
    access_token = (
        "413e37ee52fb7ea945aec3c61b5c6f0573aabd0b04dcf5476d4ad8571df165f6"
    )

    webhook_url = (
            "https://oapi.dingtalk.com/robot/send?access_token="
            + access_token
            + "&timestamp="
            + timestamp
            + "&sign="
            + sign
    )
    headers = {"Content-Type": "application/json"}
    data = {
        "msgtype": "markdown",
        "markdown": {"title": title, "text": info},
    }
    response = requests.post(webhook_url, headers=headers, data=json.dumps(data))
    return response.json()


if __name__ == '__main__':
    errorList = ["url1", "url2"]
    sendMessage("红人定期任务",
                f"## 红人表\n\n**以下链接存在问题**:\n\n" + "\n".join([f"- {url}" for url in errorList]))
