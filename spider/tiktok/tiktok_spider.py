"""
@ProjectName: DataAnalysis
@FileName：tiktok_spider.py
@IDE：PyCharm
@Author：Libre
@Time：2024/7/29 上午10:10
"""
import time
from typing import Optional

from playwright.sync_api import Page, Browser, BrowserContext, sync_playwright, Response

from log.logger import global_log
from spider.config.config import return_viewPort, user_agent, headerLess
from spider.sql.data_inner_db import inner_CelebrityProfile
from tool.download_file import download_image_file
from tool.grading_criteria import grade_criteria


class Task:
    def __init__(self, _browser: Optional[Browser], _context: BrowserContext):
        self.browser = _browser
        self.context = _context
        self.page: Optional[Page] = self.context.new_page()
        self.human_wait_time = 6000
        self.response_data = {}
        self.response_sort_data = []
        self.finish_data = {}

    def _close_data(self):
        self.response_data = {}
        self.response_sort_data = []
        self.finish_data = {}

    def verify_bar_close(self) -> None:
        """关闭验证，并更新"""
        verify_bar_item = self.page.query_selector('//*[@id="verify-bar-close"]')
        global_log.info(f"是否出现验证: {verify_bar_item}")
        if verify_bar_item:
            self.page.wait_for_timeout(self.human_wait_time)
            verify_bar_item.click()
            self.page.wait_for_timeout(self.human_wait_time)
            pass_verify_bar = self.page.query_selector('//button[text()="刷新"]')
            if pass_verify_bar:
                pass_verify_bar.click()
            self.page.wait_for_timeout(self.human_wait_time)

    def _get_user_info(self, response: Response):
        url = response.url
        if "https://www.tiktok.com/api/post/item_list/" in url:
            # 获取响应内容
            url_request_body = response.json()
            if url_request_body:
                self.response_data["item_list"] = url_request_body

    # Get page elements
    def _get_page_elements(self) -> int:
        str_fans_count = self.page.wait_for_selector('//*[@title="粉丝" or @data-e2e="followers-count"]').text_content().upper()
        if str_fans_count.endswith('K'):
            return int(float(str_fans_count[:-1]) * 1_000)  # K 代表千（1000）
        elif str_fans_count.endswith('M'):
            return int(float(str_fans_count[:-1]) * 1_000_000)  # M 代表百万（1000000）
        elif str_fans_count.endswith('B'):
            return int(float(str_fans_count[:-1]) * 1_000_000_000)  # G 代表十亿（1000000000）
        else:
            return int(str_fans_count)  # 如果没有单位，直接转换为整数

    def _get_page_response_elements(self) -> None:
        item_list_raw_data = self.response_data.get("item_list")
        item_list = item_list_raw_data.get("itemList")
        is_need_get_author = True
        likes_list = []
        comments_list = []
        views_list = []
        for item in item_list[:10]:
            if is_need_get_author:
                author_info = item.get("author")
                # avatarLarger nickname uniqueId
                self.finish_data["full_name"] = author_info.get("nickname")
                self.finish_data["user_name"] = author_info.get("uniqueId")
                self.finish_data["user_id"] = author_info.get("id")
                download_image_head_url = download_image_file(author_info.get("avatarLarger"),
                                                              author_info.get("uniqueId"))
                global_log.info(download_image_head_url)
                self.finish_data["profile_picture_url"] = download_image_head_url
                is_need_get_author = False
            stats = item.get("stats")
            views_list.append(stats.get("playCount", 0))
            likes_list.append(stats.get("diggCount", 0))
            comments_list.append(stats.get("commentCount", 0))

        self.finish_data["average_likes"] = sum(likes_list) / len(likes_list)
        self.finish_data["average_comments"] = sum(comments_list) / len(comments_list)
        self.finish_data["average_views"] = sum(views_list) / len(views_list)
        self.finish_data["average_engagement_rate"] = \
            ((self.finish_data["average_likes"] + self.finish_data["average_comments"])
             / self.finish_data["average_views"])
        self.finish_data["level"] = grade_criteria(self.finish_data["platform"], self.finish_data["average_views"])

    def work(self, _url) -> None:
        try:
            """代码执行层"""
            self.page.on("response", self._get_user_info)
            self.page.goto(_url, wait_until="domcontentloaded")
            global_log.info(f"tiktok start -> {_url}")
            self.page.wait_for_timeout(self.human_wait_time * 2)
            # 不需要登录
            pass_login = self.page.query_selector('//*[text()="以游客身份继续"]')
            if pass_login:
                pass_login.click()
            self.page.wait_for_timeout(self.human_wait_time)
            self.verify_bar_close()

            self.finish_data["index_url"] = _url
            self.finish_data["platform"] = "tiktok"
            self.finish_data["isDelete"] = 0
            self.finish_data["follower_count"] = self._get_page_elements()

            for item in range(30):
                if len(self.response_data) >= 1:
                    break
                time.sleep(1)
            if len(self.response_data) == 0:
                raise ValueError("tiktok获取数据异常")
            self._get_page_response_elements()
            inner_CelebrityProfile(self.finish_data, isById=True)
            self._close_data()
        except Exception:
            global_log.error()
            raise

    def run(self, url):
        self.work(url)


if __name__ == '__main__':
    with sync_playwright() as playwright:
        # Connect to the running browser instance
        browser = playwright.chromium.launch(
            headless=headerLess,
            channel="chrome",
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-gpu",
                "--disable-software-rasterizer"
            ]
        )
        browser_context = browser.new_context(
            viewport=return_viewPort(),
            user_agent=user_agent
        )
        Task(browser, browser_context).run('https://www.tiktok.com/@nvzion')
