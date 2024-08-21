"""
@ProjectName: Influencer_Data_Management_System
@FileName：get_ws.py
@IDE：PyCharm
@Author：Libre
@Time：2024/8/8 上午10:05
"""
import subprocess

import requests

from log.logger import LoguruLogger

log = LoguruLogger(console=True, isOpenError=True)


def start_chrome():
    chrome_command = (
        r'"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 '
        r'--user-data-dir="C:\chrome-user-data"')
    subprocess.Popen(chrome_command, shell=True)


def get_ws_id():
    try:
        response = requests.get('http://localhost:9222/json/version')
        log.info(response.text)
        webSocketDebuggerUrl = response.json().get("webSocketDebuggerUrl")
        return webSocketDebuggerUrl
    except Exception as e:
        start_chrome()
        response = requests.get('http://localhost:9222/json/version')
        log.info(response.text)
        webSocketDebuggerUrl = response.json().get("webSocketDebuggerUrl")
        return webSocketDebuggerUrl
