"""
@ProjectName: DataAnalysis
@FileName：youtube_spider.py
@IDE：PyCharm
@Author：Libre
@Time：2024/7/30 下午1:37
"""
import random
import re
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue
from typing import Optional, List

from playwright.sync_api import Page, Browser, BrowserContext, sync_playwright, ElementHandle, Route
from sqlalchemy import update, and_

from log.logger import global_log
from spider.sql.mysql import Connect
from spider.template.exception_template import RetryableError
from spider.template.spider_db_template import Base, CelebrityProfile
from tool.download_file import download_image_file
from tool.grading_criteria import convert_words_to_numbers, grade_criteria


class Task:
    def __init__(self, _browser: Browser, _context: BrowserContext):
        self.browser = _browser
        self.context = _context
        self.page: Optional[Page] = None
        for page in self.context.pages:
            if "youtube" in page.url:
                self.page = page
                break
        if self.page is None:
            self.page = _context.new_page()
        self.human_wait_time = 6000
        self.response_data = {}
        self.response_sort_data = []
        self.finish_data = {}
        self.all_urls_list = []
        self.urls_list = Queue()
        self.close_comment_flag = 10
        self.max_len = 0
        self.like = 0
        self.view = 0
        self.comment = 0
        # 数据库配置文件
        # 配置连接池
        # 创建表
        self.db = Connect(2, "marketing")
        self.db.create_session()
        Base.metadata.create_all(self.db.engine)

    def _close_data(self):
        self.response_data = {}
        self.response_sort_data = []
        self.finish_data = {}
        self.all_urls_list = []
        self.urls_list = Queue()
        self.close_comment_flag = 10
        self.max_len = 0
        self.like = 0
        self.view = 0
        self.comment = 0

    def _data_To_db(self) -> None:
        """更新数据"""
        try:
            if self.db.check_connection() is not True:
                self.db.reconnect_session()
            db_history_data = (self.db.session.query(CelebrityProfile)
                               .filter(
                and_(
                    CelebrityProfile.platform == self.finish_data.get("platform"),
                    CelebrityProfile.user_name == self.finish_data.get("user_name"),
                    )
            ).first())
            if db_history_data:
                self.db.session.execute(
                    update(CelebrityProfile)
                    .where(and_(
                        CelebrityProfile.platform == self.finish_data.get("platform"),
                        CelebrityProfile.user_name == self.finish_data.get("user_name"),
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
            self.db.session.rollback()
            raise ValueError(f"data -> {self.finish_data} exception -> {e} ")

    def get_country_item(self):
        self.page.query_selector('//yt-description-preview-view-model').click()
        self.page.wait_for_timeout(self.human_wait_time)
        # //tr[.//*[@icon="person_radar"]]
        get_person_radar_item = self.page.query_selector('//tr[.//*[@icon="person_radar"]]').text_content()
        get_person_radar_item = get_person_radar_item.replace("位订阅者", "").strip()
        follower_count = 1
        if self.has_chinese(get_person_radar_item):
            get_person_radar_str = get_person_radar_item[-1]
            numbers = convert_words_to_numbers.get(get_person_radar_str)
            cur = self.clean_and_convert(get_person_radar_item[:-1])
            follower_count = cur * numbers
        else:
            follower_count = int(get_person_radar_item)
        get_country_item = self.page.query_selector('//tr[.//*[@icon="privacy_public"]]').text_content()
        content_metadata = self.page.query_selector('//yt-content-metadata-view-model').text_content()
        metadata_list = content_metadata.split('•')
        full_name = self.page.query_selector('//yt-dynamic-text-view-model').text_content()

        self.finish_data["user_name"] = metadata_list[0].strip()
        self.finish_data["full_name"] = full_name
        self.finish_data["follower_count"] = follower_count
        self.finish_data["region"] = get_country_item.strip()
        print(self.finish_data["profile_picture_url"])
        download_image_head_url = download_image_file(self.finish_data["profile_picture_url"],
                                                      self.finish_data["user_name"])
        print(download_image_head_url)
        self.finish_data["profile_picture_url"] = download_image_head_url
        self.page.wait_for_timeout(self.human_wait_time / 2)
        self.page.query_selector('//tp-yt-paper-dialog[@role="dialog"]//button[@aria-label="关闭"]').click()
        self.page.wait_for_timeout(self.human_wait_time)

    def has_chinese(self, s):
        """检查字符串是否包含任何中文字符"""
        return bool(re.search(r'[\u4e00-\u9fff]', s))

    def get_10_video_list(self):
        video_contents: List[ElementHandle] = self.page.query_selector_all(
            '//*[@id="primary"]//*[@id="contents"]//ytd-thumbnail[@size="large"]/a')
        for video in video_contents:
            video_url = video.get_attribute("href")
            self.all_urls_list.append("https://www.youtube.com" + video_url)
        for _ in self.all_urls_list[:10]:
            self.urls_list.put(_)
        self.max_len = self.urls_list.qsize()

    def clean_and_convert(self, s):
        """
        清理字符串中的非数字字符并将其转换为整数。
        :param s: 原始字符串
        :return: 转换后的整数值，如果转换失败则返回 None
        """
        # 去除字符串中的空格和换行符
        s = s.strip()

        # 去除非数字字符（保留小数点和千位分隔符）
        s = ''.join(filter(lambda x: x.isdigit() or x in ['.', ','], s))

        # 替换千位分隔符
        s = s.replace(',', '')

        try:
            # 将清理后的字符串转换为浮点数（可以处理千位分隔符）
            return float(s)
        except ValueError:
            return None  # 或者返回一个合适的默认值

    def extract_number(self, text) -> Optional[float]:
        """提取并转换字符串中的数字"""
        if self.has_chinese(text):
            match_str = text[-1]
            numbers = convert_words_to_numbers.get(match_str)  # 默认为 1 如果未找到
            if numbers is None:
                raise ValueError(f"字段替换数字报错 {text} {match_str}")
            return self.clean_and_convert(text[:-1]) * numbers
        else:
            return self.clean_and_convert(text)

    def block_media_requests(self, route: Route, request):
        url = request.url
        if url.endswith('.jpg') or url.endswith('.png') or 'video' in url:
            route.abort()  # 拦截并阻止请求
        else:
            route.continue_()  # 继续其他请求

    def process_page(self, page_url, threading_event: threading.Event):

        """页面处理"""
        with (sync_playwright() as _playwright):
            try:
                cur_browser = _playwright.chromium.launch(
                    headless=False,
                    channel="chrome",
                    args=["--disable-blink-features=AutomationControlled"],
                )
                cur_context = cur_browser.new_context()

                cur_context.add_init_script(
                    "const newProto = navigator.__proto__; delete newProto.webdriver; navigator.__proto__ = newProto;"
                )
                page = cur_context.new_page()
                # 设置拦截器
                page.route('**/*', self.block_media_requests)

                like_count = None
                view_count = None
                comment_count = None
                try:
                    page.goto(page_url, wait_until="domcontentloaded")
                except Exception:
                    ...

                while True:
                    fold = page.query_selector('//div[@id="above-the-fold"]')

                    if fold is not None:
                        break
                    page.wait_for_timeout(self.human_wait_time)

                feedback = page.query_selector('//*[@id="yt-spec-touch-feedback-shape__fill"]')

                if feedback is not None:
                    feedback.click()
                page.wait_for_timeout(self.human_wait_time)
                like_button_view_model = page.query_selector(
                    '//like-button-view-model//div[@class="yt-spec-button-shape-next__button-text-content"]')
                if like_button_view_model:
                    global_log.info("url: " + page_url + "点赞：" + like_button_view_model.text_content())
                    # //like-button-view-model/toggle-button-view-model/button-view-model[@class="yt-spec-button-view-model"]/button
                    # aria-label="与另外 433 人一起赞此视频"
                    like_count_str = like_button_view_model.text_content()
                    if "赞" in like_count_str:
                        like_count_str = "0"

                    if "12345678901234567890123456789" in like_button_view_model.text_content():
                        aria_label = page.query_selector(
                            '//like-button-view-model/toggle-button-view-model/button-view-model[@class="yt-spec-button-view-model"]/button').get_attribute(
                            "aria-label")
                        like_count_str = aria_label.replace("与另外", "").replace("人一起赞此视频", "").strip()
                    like_count = self.extract_number(like_count_str)
                view_info = page.query_selector('//div[@id="info-container"]//yt-formatted-string[@id="info"]')
                if view_info:
                    global_log.info("观看量：" + view_info.text_content())
                    view_info_str = view_info.text_content().split("次观看")[0]
                    view_count = self.extract_number(view_info_str)
                # 滚动到页面底部
                # while True:
                page.wait_for_timeout(self.human_wait_time)
                page.mouse.wheel(0, random.randint(300, 500))
                page.wait_for_load_state("domcontentloaded")
                for _ in range(5):
                    page.wait_for_timeout(self.human_wait_time)

                    if page.query_selector('//*[text()="评论已关闭。"]') is not None:
                        threading_event.set()
                        return

                    commend_info = page.query_selector('//div[@id="leading-section"]//span')
                    if commend_info is not None:
                        if "评论" in commend_info.text_content():
                            commend_info = page.query_selector('//div[@id="leading-section"]//span[2]')
                        global_log.info("评论：" + commend_info.text_content())
                        comment_count = self.extract_number(commend_info.text_content())
                        break

                if like_count is not None \
                        and view_count is not None \
                        and comment_count is not None:
                    self.like += like_count
                    self.view += view_count
                    self.comment += comment_count
                else:
                    raise RetryableError(f"like_count:{like_count}, "
                                         f"view_count:{view_count}, "
                                         f"comment_count:{comment_count}")
            except Exception:
                raise

    def work(self, _url):
        if "videos" not in _url:
            _url = _url.removesuffix('/') + "/videos"
        global_log.info(_url)
        self.page.goto(_url, wait_until="domcontentloaded")
        self.page.wait_for_timeout(self.human_wait_time)
        get_profile_pic_item = self.page.query_selector('//yt-avatar-shape//img').get_attribute("src")
        self.finish_data["profile_picture_url"] = get_profile_pic_item
        self.get_country_item()
        self.page.wait_for_timeout(self.human_wait_time)
        self.get_10_video_list()
        # 增加并发速 5 -> 稳定
        while self.urls_list.empty() is False:
            with ThreadPoolExecutor(max_workers=10) as executor:

                future_to_url = {}
                """映射 Future 对象到任务"""
                for _ in range(self.urls_list.qsize()):  # 最多提交10个任务
                    # 每一个线程都有独立的线程任务
                    threading_event = threading.Event()
                    url = self.urls_list.get()
                    future_to_url[executor.submit(self.process_page, url, threading_event)] = url

                for future in as_completed(future_to_url):
                    retry_url = future_to_url[future]
                    try:
                        # 超时5分钟
                        future.result(timeout=60 * 5)  # 确保获取任务的结果并处理异常
                    except RetryableError:
                        print(retry_url)
                        self.urls_list.put(retry_url)
                    except Exception as e:
                        raise

                    # 跳过本轮计算 -> 自动归为False
                    if threading_event.is_set():
                        self.close_comment_flag = self.close_comment_flag + 1
                        self.urls_list.put(self.all_urls_list[self.close_comment_flag])
                        threading_event.clear()
                        continue

        self.finish_data["index_url"] = _url
        self.finish_data["platform"] = "youtube"
        self.finish_data["average_likes"] = self.like / self.max_len
        self.finish_data["average_views"] = self.view / self.max_len
        self.finish_data["average_comments"] = self.comment / self.max_len
        self.finish_data["average_engagement_rate"] = (
                (self.finish_data["average_likes"] + self.finish_data["average_comments"])
                / self.finish_data["average_views"])

        self.finish_data["level"] = grade_criteria("youtube", self.finish_data["average_views"])
        self._data_To_db()
        self._close_data()

    def run(self, url):
        self.work(url)


if __name__ == '__main__':
    with sync_playwright() as playwright:
        # Connect to the running browser instance
        browser = playwright.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0]
        Task(browser, context).run('https://www.youtube.com/@HansTechTalk/videos')
