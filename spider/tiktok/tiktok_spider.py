"""
@ProjectName: DataAnalysis
@FileName：tiktok_spider.py
@IDE：PyCharm
@Author：Libre
@Time：2024/7/29 上午10:10
"""
from typing import Optional

from playwright.sync_api import Page, Browser, BrowserContext, sync_playwright, Response
from sqlalchemy import update, and_

from log.logger import LoguruLogger
from spider.sql.mysql import Connect
from spider.template.spider_db_template import Base, CelebrityProfile
from tool.grading_criteria import grade_criteria

log = LoguruLogger(console=True, isOpenError=True)


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
        self.human_wait_time = 6000
        self.response_data = {}
        self.response_sort_data = []
        self.finish_data = {}

        # 配置连接池
        # 创建表
        self.db = Connect(2, "marketing")
        self.db.create_session()
        Base.metadata.create_all(self.db.engine)

    def _close_data(self):
        self.response_data = {}
        self.response_sort_data = []
        self.finish_data = {}

    def _data_To_db(self) -> None:
        """更新数据"""
        try:
            if not self.db.check_connection():
                self.db.reconnect_session()
            db_history_data = (self.db.session.query(CelebrityProfile)
                               .filter(
                and_(
                    CelebrityProfile.platform == self.finish_data.get("platform"),
                    CelebrityProfile.user_id == self.finish_data.get("user_id"),
                )
            ).first())
            if db_history_data:
                self.db.session.execute(
                    update(CelebrityProfile)
                    .where(and_(
                        CelebrityProfile.platform == self.finish_data.get("platform"),
                        CelebrityProfile.user_id == self.finish_data.get("user_id"),
                    ))
                    .values(self.finish_data)
                )
            else:
                instagram_profile = CelebrityProfile(
                    **self.finish_data
                )
                self.db.session.add(instagram_profile)
            self.db.session.commit()
        except Exception as e:
            log.error(f"Failed to log to database: {e}")
            self.db.session.rollback()

    def verify_bar_close(self) -> None:
        """关闭验证，并更新"""
        verify_bar_item = self.page.query_selector('//*[@id="verify-bar-close"]')
        print(verify_bar_item)
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
        str_fans_count = self.page.wait_for_selector('//*[@title="粉丝"]').text_content().upper()
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
                self.finish_data["profile_picture_url"] = author_info.get("avatarLarger")
                self.finish_data["full_name"] = author_info.get("nickname")
                self.finish_data["user_name"] = author_info.get("uniqueId")
                self.finish_data["user_id"] = author_info.get("id")
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
        """代码执行层"""
        self.page.on("response", self._get_user_info)
        self.page.goto(_url, wait_until="domcontentloaded")
        self.page.wait_for_timeout(self.human_wait_time * 2)
        # 不需要登录
        pass_login = self.page.query_selector('//*[text()="以游客身份继续"]')
        if pass_login:
            pass_login.click()
        self.page.wait_for_timeout(self.human_wait_time)
        self.verify_bar_close()

        self.finish_data["index_url"] = _url
        self.finish_data["platform"] = "tiktok"
        self.finish_data["follower_count"] = self._get_page_elements()

        while True:
            if len(self.response_data) == 1:
                break

        self._get_page_response_elements()
        self._data_To_db()

    def run(self, url):
        self.work(url)


if __name__ == '__main__':
    with sync_playwright() as playwright:
        # Connect to the running browser instance
        browser = playwright.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0]
        Task(browser, context).run()
