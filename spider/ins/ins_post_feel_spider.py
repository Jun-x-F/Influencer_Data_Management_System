"""
@ProjectName: DataAnalysis
@FileName：ins_post_feel_spider.py
@IDE：PyCharm
@Author：Libre
@Time：2024/8/1 下午5:41
"""
import json
import re
import time
from typing import Optional
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright, Response

from log.logger import global_log
from spider.config.config import redis_conn, executable_path, headerLess
from spider.ins.ins_new import get_ins_info, save_cookies, random_account_
from spider.sql.data_inner_db import inner_InfluencersVideoProjectData, inner_InfluencersVideoProjectDataByDate
from tool.JsonUtils import dfs_get_value
from tool.TimeUtils import TimeUtils


class Task:
    def __init__(self, _browser: Optional[Browser], _context: BrowserContext, page: Page, account, password, code, isCheckLogin):
        self.browser:Optional[Browser] = _browser
        self.context = _context
        self.page = page
        self.account = account
        self.password = password
        self.code = code
        self.isCheckLogin = isCheckLogin
        self.human_wait_time = 6000
        self.finish_data = {}
        self.cur_html: Optional[str] = None
        self.cur_url: Optional[str] = None

    def _close(self):
        self.finish_data = {}

    def on_response(self, response: Response):
        url = response.url
        if self.cur_url in url:
            self.cur_html = response.text()

    def extract_script_with_like_count(self, html_content):
        # 解析 HTML 内容
        soup = BeautifulSoup(html_content, 'lxml')

        # 找到所有的 <script> 标签
        script_tags = soup.find_all('script')

        # 筛选出包含 "like_count" 的 <script> 标签
        script_with_like_count = [script for script in script_tags if
                                  "like_count" in script.get_text()
                                  and ("adp_PolarisPostRootDirectQueryRelayPreloader_" in script.get_text()
                                       or "adp_PolarisPostRootQueryRelayPreloader_" in script.get_text())]
        # 返回包含 "like_count" 的 <script> 标签列表
        return script_with_like_count

    def fetch_data(self):
        # 提取 <script> 标签
        scripts = self.extract_script_with_like_count(self.cur_html)

        global_log.info(f"{self.cur_url}获取到scripts：{len(scripts)}个")

        if len(scripts) != 1:
            global_log.error(f"{self.cur_url}\n{repr(scripts)}")
            raise ValueError("获取到scripts出现多个，注意排除")

        script_json = json.loads(scripts[0].text)
        # input(script_json)
        taken_at = dfs_get_value(script_json, "taken_at")
        username = dfs_get_value(script_json, "username", parent="user")

        dt = TimeUtils.timestamp_to_datetime(taken_at)
        releasedTime = TimeUtils.format_datetime(dt)

        self.finish_data["user_name"] = username
        self.finish_data["releasedTime"] = releasedTime
        _type = self.set_platform(self.cur_url)
        if _type == "视频":
            return f"https://www.instagram.com/{username}/reels"
        else:
            return f"https://www.instagram.com/{username}"

    @staticmethod
    def extract_username(cur_url):
        """
        从 Instagram URL 中提取用户名
        """
        pattern = r"https?://(?:www\.)?instagram\.com/reel/([A-Za-z0-9._-]+)/?"
        post_pattern = r"https?://(?:www\.)?instagram\.com/p/([A-Za-z0-9_-]+)/?$"
        match = re.match(pattern, cur_url)
        post_math = re.match(post_pattern, cur_url)
        if match:
            return match.group(1)
        elif post_math:
            return post_math.group(1)
        else:
            raise ValueError("Invalid Instagram URL")

    @staticmethod
    def extract_post_id(cur_url):
        """
        从 Instagram URL 中提取帖子或短视频的 ID
        """
        # 解析 URL
        try:
            parsed_url = urlparse(cur_url)
        except Exception as e:
            raise ValueError(f"Invalid URL: {e}")

        # 提取路径部分
        path = parsed_url.path.strip('/')

        # 定义不同类型的 URL 模式
        patterns = [
            r"^p/([A-Za-z0-9_-]{11})/?",  # 帖子
            r"^reel/([A-Za-z0-9._-]{11})/?",  # 短视频
            r"^shorts/([A-Za-z0-9_-]{11})/?"  # Shorts
        ]

        for pattern in patterns:
            match = re.match(pattern, path)
            if match:
                return match.group(1)

        raise ValueError("Invalid Instagram URL format")

    @staticmethod
    def set_platform(url):
        if "reel" in url:
            return "视频"
        else:
            return "图片"

    def work(self):
        self.page.on("response", self.on_response)
        self.page.goto(self.cur_url, wait_until="domcontentloaded")
        self.page.wait_for_timeout(self.human_wait_time)
        is_error = True
        for _ in range(30):
            if self.cur_html is not None:
                is_error = False
                break
            time.sleep(1)
        if is_error is True:
            raise ValueError(f"获取不到{self.cur_url}的html信息")
        cur_url = self.fetch_data()
        cur_code = self.extract_post_id(self.cur_url)
        save_cookies(self.page, f"ins_{self.account}_cookies")
        return cur_code, cur_url, self.finish_data

    def run(self, url):
        self.cur_url = url.split("?")[0]
        return self.work()


def ins_videos_start_spider(url):
    """新的启动器"""
    get_ins_media_code = get_ins_media_url = get_ins_media_info = None
    account_info = random_account_()
    # {'user': 'danielkroesche94', 'password': 'Provia312CH@@123', 'code': 'IU4X NUVZ E5HJ ZMTL AYYD RWJC 7D63 TGW2', 'fileDir': 'C:\\browser\\ins\\chrome-danielkroesche94-data', 'port': 9225}

    user = account_info.get("user")
    password = account_info.get("password")
    code = account_info.get("code")
    port = account_info.get("port")
    fileDir = account_info.get("fileDir")
    # ws_id = get_ws_id(port, fileDir)

    global_log.info(f"ins 视频 -> 获取到对应的账号为 {account_info}...")
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch_persistent_context(
            executable_path=executable_path,  # 指定使用谷歌浏览器进行配置
            user_data_dir=fileDir,  # 指定用户数据目录
            headless=headerLess,  # 确保浏览器不是无头模式
            args=["--disable-blink-features=AutomationControlled"]  # 避免自动化检测
        )
        # cdp = playwright.chromium.connect_over_cdp(ws_id)
        # contexts = cdp.contexts[0]
        cur_cookies = f"ins_{user}_cookies"
        cookies_str = redis_conn.get_value(cur_cookies)
        isCheckLogin = True
        if cookies_str is not None:
            cookies = json.loads(cookies_str)
            # 重新update
            browser.add_cookies(cookies)
            isCheckLogin = False
        browser.add_init_script(
            "const newProto = navigator.__proto__; delete newProto.webdriver; navigator.__proto__ = newProto;"
        )
        for cur_page in browser.pages:
            # 页面清除
            if "instagram" in cur_page.url:
                cur_page.close()
        _page = browser.new_page()
        get_ins_media_code, get_ins_media_url, get_ins_media_info = \
            Task(None, browser, _page, user, password, code, isCheckLogin).run(url)
        browser.close()
    key = Task.extract_post_id(url)
    value_str = redis_conn.get_value(key)
    if value_str is None:
        # 修改对应的数据 => 将他修改为读取当前的cookies和browser、page
        item_json = get_ins_info(code=get_ins_media_code, url=get_ins_media_url, fileDir=fileDir, cur_cookies=cur_cookies)
        item_data = item_json.get(key)
    else:
        item_data = json.loads(value_str)

    try:
        engagement_rate = ((item_data.get("comment_count", 0) + item_data.get("like_count", 0))
                           / item_data.get("play_count", 0))
    except Exception:
        if item_data is None:
            item_data = {}
        engagement_rate = 0
    res_data = {
        "platform": "instagram",
        "type": Task.set_platform(url),
        "likes": item_data.get("like_count", 0),
        "comments": item_data.get("comment_count", 0),
        "views": item_data.get("play_count", 0),
        "engagement_rate": engagement_rate,
        "user_name": get_ins_media_info.get("user_name"),
        "full_name": get_ins_media_info.get("user_name"),
        "releasedTime": get_ins_media_info.get("releasedTime"),
        "video_url": url,
    }
    global_log.info(f"ins 视频 ==> {res_data}")
    inner_InfluencersVideoProjectData(res_data)
    inner_InfluencersVideoProjectDataByDate(res_data)


if __name__ == '__main__':
    ins_videos_start_spider("https://www.instagram.com/reel/C6yMBY0yb0S/")
    # print(Task.extract_post_id("https://www.instagram.com/p/C-uAo_4uvWe/?img_index=1"))
