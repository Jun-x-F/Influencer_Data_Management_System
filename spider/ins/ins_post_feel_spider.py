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

from bs4 import BeautifulSoup
from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright, Response

from log.logger import global_log
from spider.config.config import headerLess, return_viewPort, user_agent, redis_conn, ins_cookies
from spider.ins.ins_new import get_ins_info
from spider.sql.data_inner_db import inner_InfluencersVideoProjectData, inner_InfluencersVideoProjectDataByDate
from tool.JsonUtils import dfs_get_value
from tool.TimeUtils import TimeUtils


class Task:
    def __init__(self, _browser: Browser, _context: BrowserContext, _page: Page):
        self.browser = _browser
        self.context = _context
        self.page = _page
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
        print(script_with_like_count)
        # 返回包含 "like_count" 的 <script> 标签列表
        return script_with_like_count

    def fetch_data(self):
        # 提取 <script> 标签
        scripts = self.extract_script_with_like_count(self.cur_html)

        global_log.info(f"{self.cur_url}获取到scripts：{len(scripts)}个")
        for script in scripts:
            global_log.info(script)
        if len(scripts) != 1:
            global_log.error(f"{self.cur_url}\n{repr(scripts)}")
            raise ValueError("获取到scripts出现多个，注意排除")

        script_json = json.loads(scripts[0].text)
        taken_at = dfs_get_value(script_json, "taken_at")
        username = dfs_get_value(script_json, "username", parent="user")

        dt = TimeUtils.timestamp_to_datetime(taken_at)
        releasedTime = TimeUtils.format_datetime(dt)

        self.finish_data["user_name"] = username
        self.finish_data["releasedTime"] = releasedTime
        return f"https://www.instagram.com/{username}/reels"

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
        cur_code = self.extract_username(self.cur_url)
        return cur_code, cur_url, self.finish_data

    def run(self, url):
        self.cur_url = url.split("?")[0]
        return self.work()


def ins_videos_start_spider(url):
    """新的启动器"""
    get_ins_media_code = get_ins_media_url = get_ins_media_info = None
    with sync_playwright() as playwright:
        ins_videos_browser = playwright.chromium.launch(
            headless=headerLess,
            channel="chrome",
            args=["--disable-blink-features=AutomationControlled"],
        )
        ins_videos_context = ins_videos_browser.new_context(viewport=return_viewPort(),
                                                            user_agent=user_agent, )

        with open(ins_cookies, 'r') as file:
            cookies = json.load(file)

        ins_videos_context.add_cookies(cookies)
        ins_videos_context.add_init_script(
            "const newProto = navigator.__proto__; delete newProto.webdriver; navigator.__proto__ = newProto;"
        )
        ins_videos_page = ins_videos_context.new_page()
        get_ins_media_code, get_ins_media_url, get_ins_media_info = \
            Task(ins_videos_browser, ins_videos_context, ins_videos_page).run(
                url)
    key = Task.extract_username(url)
    value_str = redis_conn.get_value(key)
    if value_str is None:
        item_json = get_ins_info(code=get_ins_media_code, url=get_ins_media_url)
        item_data = item_json.get(key)
    else:
        item_data = json.loads(value_str)
    engagement_rate = 0
    try:
        engagement_rate = ((item_data.get("comment_count", 0) + item_data.get("like_count", 0))
                           / item_data.get("play_count", 0))
    except TypeError and ZeroDivisionError:
        engagement_rate = 0
    res_data = {
        "platform": "instagram",
        "type": Task.set_platform(url),
        "likes": item_data.get("like_count"),
        "comments": item_data.get("comment_count"),
        "views": item_data.get("play_count"),
        "engagement_rate": engagement_rate,
        "user_name": get_ins_media_info.get("user_name"),
        "releasedTime": get_ins_media_info.get("releasedTime"),
        "video_url": url,
    }
    global_log.info(res_data)
    inner_InfluencersVideoProjectData(res_data)
    inner_InfluencersVideoProjectDataByDate(res_data)
