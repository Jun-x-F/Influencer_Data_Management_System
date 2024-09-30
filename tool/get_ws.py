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


def start_chrome(port, file_dir):
    chrome_command = (
        rf'"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port={port} '
        rf'--user-data-dir={file_dir}')
    subprocess.Popen(chrome_command, shell=True)


def get_ws_id(port=9222, file_dir=r"C:\chrome-user-data"):
    try:
        response = requests.get(f'http://localhost:{port}/json/version')
        log.info(response.text)
        webSocketDebuggerUrl = response.json().get("webSocketDebuggerUrl")
        return webSocketDebuggerUrl
    except Exception as e:
        start_chrome(port, file_dir)
        response = requests.get(f'http://localhost:{port}/json/version')
        log.info(response.text)
        webSocketDebuggerUrl = response.json().get("webSocketDebuggerUrl")
        return webSocketDebuggerUrl
