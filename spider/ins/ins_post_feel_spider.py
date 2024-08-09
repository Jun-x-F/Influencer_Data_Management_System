"""
@ProjectName: DataAnalysis
@FileName：ins_post_feel_spider.py
@IDE：PyCharm
@Author：Libre
@Time：2024/8/1 下午5:41
"""
from typing import Optional

from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright, Response
from sqlalchemy import update, and_

from log.logger import LoguruLogger
from spider.sql.mysql import Connect
from spider.template.spider_db_template import Base, InfluencersVideoProjectData
from tool.TimeUtils import TimeUtils

log = LoguruLogger(console=True, isOpenError=True)


class Task:
    def __init__(self, _browser: Browser, _context: BrowserContext):
        self.browser = _browser
        self.context = _context
        self.page: Optional[Page] = None
        for page in self.context.pages:
            if "instagram" in page.url:
                self.page = page
                break
        if self.page is None:
            self.page = self.context.new_page()
        self.human_wait_time = 6000
        self.response_data = {}
        self.response_sort_data = []
        self.finish_data = {}

        # 数据库配置文件
        # 配置连接池
        # 创建表
        self.db = Connect(2, "marketing")
        self.db.create_session()
        Base.metadata.create_all(self.db.engine)

    def _close(self):
        self.response_data = {}
        self.response_sort_data = []
        self.finish_data = {}

    def on_response(self, response: Response):
        url = response.url
        # https://www.instagram.com/graphql/query --> PolarisPostActionLoadPostQueryQuery
        if "https://www.instagram.com/graphql/query" == url:
            post_data = response.request.post_data_json
            if post_data:
                fb_api_req_friendly_name = post_data.get("fb_api_req_friendly_name", None)
                if fb_api_req_friendly_name == "PolarisPostActionLoadPostQueryQuery":
                    self.response_data["fetch"] = response.json()

    def fetch_data(self):
        data = self.response_data.get("fetch").get("data")
        xdt_shortcode_media = data.get("xdt_shortcode_media")
        views = xdt_shortcode_media.get("video_play_count") if xdt_shortcode_media.get("video_play_count") != -1 else 0
        owner = xdt_shortcode_media.get("owner")
        username = owner.get("username")
        edge_media_preview_comment = xdt_shortcode_media.get("edge_media_preview_comment")
        comments = edge_media_preview_comment.get("count") if edge_media_preview_comment.get("count") != -1 else 0
        edge_media_preview_like = xdt_shortcode_media.get("edge_media_preview_like")
        likes = edge_media_preview_like.get("count") if edge_media_preview_like.get("count") != -1 else 0
        try:
            engagement_rate = (comments + likes) / views
            self.finish_data["engagement_rate"] = engagement_rate
        except TypeError:
            ...
        taken_at_timestamp = xdt_shortcode_media.get("taken_at_timestamp")
        dt = TimeUtils.timestamp_to_datetime(taken_at_timestamp)
        releasedTime = TimeUtils.format_datetime(dt)

        self.finish_data["user_name"] = username
        self.finish_data["releasedTime"] = releasedTime
        self.finish_data["views"] = views
        self.finish_data["likes"] = likes
        self.finish_data["comments"] = comments

    def _data_To_db(self) -> None:
        """更新数据"""
        try:
            if not self.db.check_connection():
                self.db.reconnect_session()
            db_history_data = (self.db.session.query(InfluencersVideoProjectData)
                               .filter(
                and_(
                    InfluencersVideoProjectData.platform == self.finish_data.get("platform"),
                    InfluencersVideoProjectData.user_name == self.finish_data.get("user_name"),
                )
            ).first())
            if db_history_data:
                self.db.session.execute(
                    update(InfluencersVideoProjectData)
                    .where(and_(
                        InfluencersVideoProjectData.platform == self.finish_data.get("platform"),
                        InfluencersVideoProjectData.user_name == self.finish_data.get("user_name"),
                    ))
                    .values(self.finish_data)
                )
            else:
                instagram_profile = InfluencersVideoProjectData(
                    **self.finish_data
                )
                self.db.session.add(instagram_profile)
            self.db.session.commit()
        except Exception as e:
            log.error(f"Failed to log to database: {e}")
            self.db.session.rollback()

    def work(self, _url):
        self.page.on("response", self.on_response)
        self.page.goto(_url, wait_until="domcontentloaded")
        self.page.wait_for_timeout(12000)
        self.finish_data["video_url"] = _url
        self.finish_data["platform"] = "instagram"
        if "reel" in _url:
            self.finish_data["type"] = "视频"
        else:
            self.finish_data["type"] = "图片"

        while True:
            if len(self.response_data.keys()) == 1:
                break

        self.fetch_data()
        self._data_To_db()
        self._close()

    def run(self, url):
        # urls = ["https://www.instagram.com/p/C-CbffAxJQ0/?img_index=1",
        #         "https://www.instagram.com/reel/C2q_hMArrKS/",
        #         "https://www.instagram.com/reel/C2uhywOAQPX/",
        #         "https://www.instagram.com/reel/C2uhtuuuYB5/",
        #         "https://www.instagram.com/reel/C4dFoI5Lwn5/",
        #         "https://www.instagram.com/reel/C40TfertqL_/"]
        # for url in urls:
        self.work(url)

    def run_upload(self, url, dc):
        self.finish_data.update(dc)
        self.work(url)


if __name__ == '__main__':
    proxy_url = f"https://brd-customer-hl_c99584d5-zone-datacenter_proxy1:8wt7q8p6682f@brd.superproxy.io:22225"
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=False,
            channel="chrome",
            args=["--disable-blink-features=AutomationControlled"],
            # proxy={
            #     'server': proxy_url,
            #     'username': 'brd-customer-hl_c99584d5-zone-datacenter_proxy1',
            #     'password': '8wt7q8p6682f',
            # }
        )
        context = browser.new_context()

        context.add_init_script(
            "const newProto = navigator.__proto__; delete newProto.webdriver; navigator.__proto__ = newProto;"
        )
        Task(browser, context).run("https://www.instagram.com/p/C-CbffAxJQ0/?img_index=1")
