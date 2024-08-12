"""
@ProjectName: DataAnalysis
@FileName：tiktok_video_spider.py
@IDE：PyCharm
@Author：Libre
@Time：2024/8/1 下午4:11
"""
import json
from typing import Optional

from bs4 import BeautifulSoup
from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright

from spider.sql.data_inner_db import inner_InfluencersVideoProjectData, inner_InfluencersVideoProjectDataByDate
from tool.TimeUtils import TimeUtils


class Task:
    def __init__(self, _browser: Browser, _context: BrowserContext):
        self.browser = _browser
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
        self.page.goto("https://www.tiktok.com", wait_until="domcontentloaded")
        self.page.wait_for_timeout(6000)
        h5 = self.page.request.get(_url).text()

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
        stats = itemStruct.get("stats")
        self.finish_data["video_url"] = _url
        self.finish_data["platform"] = "tiktok"
        self.finish_data["user_name"] = uniqueId
        self.finish_data["type"] = "视频"
        self.finish_data["releasedTime"] = formatted_time
        self.finish_data["views"] = stats.get("playCount")
        self.finish_data["comments"] = stats.get("commentCount")
        self.finish_data["forward"] = stats.get("shareCount")
        self.finish_data["likes"] = stats.get("diggCount")
        self.finish_data["collections"] = stats.get("collectCount")
        self.finish_data["engagement_rate"] = ((self.finish_data["likes"] + self.finish_data["comments"])
                                               / self.finish_data["views"])
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
        browser = playwright.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0]
        Task(browser, context).run()
