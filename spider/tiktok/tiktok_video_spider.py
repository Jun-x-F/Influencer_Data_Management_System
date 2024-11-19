"""
@ProjectName: DataAnalysis
@FileName：tiktok_video_spider.py
@IDE：PyCharm
@Author：Libre
@Time：2024/8/1 下午4:11
"""
import json
from typing import Optional

import requests
from bs4 import BeautifulSoup
from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright

from log.logger import global_log
from spider.config.config import return_viewPort, user_agent
from spider.sql.data_inner_db import inner_InfluencersVideoProjectData, inner_InfluencersVideoProjectDataByDate
from tool.TimeUtils import TimeUtils


class Task:
    def __init__(self, _browser: Optional[Browser], _context: BrowserContext):
        self.browser: Optional[Browser] = _browser
        self.context = _context
        self.page: Optional[Page] = None
        for page in self.context.pages:
            if "tiktok" in page.url:
                self.page = page
                break
        if self.page is None:
            self.page = self.context.new_page()
        self.finish_data = {}

    def _close_data(self):
        self.finish_data = {}

    def work(self, _url):
        self.page.goto(_url, wait_until="domcontentloaded")
        self.page.wait_for_timeout(12000)
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "zh-CN,zh;q=0.9",
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "priority": "u=0, i",
            "sec-ch-ua": "\"Chromium\";v=\"130\", \"Google Chrome\";v=\"130\", \"Not?A_Brand\";v=\"99\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
        }
        cookies = {}
        for cookie in self.page.context.cookies():
            cookies[cookie["name"]] = cookie["value"]
        response = requests.get(url=_url, cookies=cookies, headers=headers)
        # input(response.text)
        h5 = response.text

        soup = BeautifulSoup(h5, 'lxml')
        script_tag = soup.find('script', {'id': '__UNIVERSAL_DATA_FOR_REHYDRATION__'})
        raw_data = json.loads(script_tag.string)
        __DEFAULT_SCOPE__ = raw_data.get("__DEFAULT_SCOPE__")
        webapp_video_detail = __DEFAULT_SCOPE__.get("webapp.video-detail")
        itemInfo = webapp_video_detail.get("itemInfo")
        itemStruct = itemInfo.get("itemStruct")
        createTime = itemStruct.get("createTime")
        dt = TimeUtils.timestamp_to_datetime(createTime)
        formatted_time = TimeUtils.format_datetime(dt)

        author = itemStruct.get("author")
        uniqueId = author.get("uniqueId")
        nickname = author.get("nickname")
        stats = itemStruct.get("stats")
        self.finish_data["video_url"] = _url
        self.finish_data["platform"] = "tiktok"
        self.finish_data["user_name"] = uniqueId
        self.finish_data["full_name"] = nickname
        self.finish_data["type"] = "视频"
        self.finish_data["releasedTime"] = formatted_time
        self.finish_data["views"] = stats.get("playCount")
        self.finish_data["comments"] = stats.get("commentCount")
        self.finish_data["forward"] = stats.get("shareCount")
        self.finish_data["likes"] = stats.get("diggCount")
        self.finish_data["collections"] = stats.get("collectCount")
        self.finish_data["engagement_rate"] = ((self.finish_data["likes"] + self.finish_data["comments"])
                                               / self.finish_data["views"])
        global_log.info(f"tiktok -> {self.finish_data}")
        inner_InfluencersVideoProjectData(self.finish_data)
        inner_InfluencersVideoProjectDataByDate(self.finish_data)
        self._close_data()

    def run(self, _url):
        # urls = ["https://www.tiktok.com/@gzwx3650/video/7367169857227459841",
        #         "https://www.tiktok.com/@thejunglebadger/video/7395298474658516257",
        #         "https://www.tiktok.com/@vladalee777/video/7365074940854357280",
        #         "https://www.tiktok.com/@se7enbaby77/video/7395110963332140293",
        #         "https://www.tiktok.com/@rainrian88665/video/7394057862382767366"]
        # for _url in urls:
        self.work(_url)

    def run_upload(self, url, dc):
        self.finish_data.update(dc)
        self.work(url)


if __name__ == '__main__':
    with sync_playwright() as playwright:
        # Connect to the running browser instance
        browser = playwright.chromium.launch(
            env={
                "LANG": "zh_CN.UTF-8",
                "LC_ALL": "zh_CN.UTF-8",
            },
            headless=False,
            channel="chrome",
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
                "--enable-automation=false",
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-gpu",
                "--disable-software-rasterizer",
            ]
        )
        browser_context = browser.new_context(
            viewport=return_viewPort(),
            user_agent=user_agent,
            extra_http_headers={
                "Accept-Language": "zh-CN,zh;q=0.9",
            },
        )
        browser_context.add_init_script(
            """
                const newProto = navigator.__proto__; delete newProto.webdriver; navigator.__proto__ = newProto;"
                 Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                 Object.defineProperty(navigator, 'languages', { get: () => ['zh-CN', 'zh'] });
                 Object.defineProperty(navigator, 'language', { get: () => 'zh-CN' });
                 Object.defineProperty(navigator, 'platform', { get: () => 'Win32' });
                 Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
           """
        )
        Task(browser, browser_context).run("https://www.tiktok.com/@bbbigdeer/video/7329382270496804139")
