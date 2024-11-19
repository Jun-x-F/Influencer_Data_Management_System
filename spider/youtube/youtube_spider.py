"""
@ProjectName: DataAnalysis
@FileName：youtube_spider.py
@IDE：PyCharm
@Author：Libre
@Time：2024/7/30 下午1:37
"""
import random
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue
from typing import Optional, List

from playwright.sync_api import Page, Browser, BrowserContext, sync_playwright, ElementHandle, Route

from log.logger import global_log
from spider.config.config import headerLess, return_viewPort, user_agent, executable_path
from spider.sql.data_inner_db import inner_CelebrityProfile
from spider.template.exception_template import RetryableError
from spider.template.notFoundData import NotUserData
from spider.youtube.youtube_public_func import get_view_count, get_like_count, get_comment_count, has_chinese, \
    clean_and_convert
from tool.download_file import download_image_file
from tool.grading_criteria import convert_words_to_numbers, grade_criteria


class Task:
    def __init__(self, _browser: Optional[Browser], _context: BrowserContext):
        self.browser: Optional[Browser] = _browser
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

    def get_country_item(self):
        try:
            self.page.query_selector('//yt-description-preview-view-model').click()
            self.page.wait_for_timeout(self.human_wait_time)
            # //tr[.//*[@icon="person_radar"]]
            get_person_radar_item = self.page.query_selector('//tr[.//*[@icon="person_radar"]]').text_content()
            get_person_radar_item = get_person_radar_item.replace("位订阅者", "").strip()
            get_person_radar_item = get_person_radar_item.replace("人", "").strip()
            get_person_radar_item = get_person_radar_item.replace(" subscribers", "").strip()
            follower_count = 1
            get_person_radar_str = get_person_radar_item[-1]
            numbers = convert_words_to_numbers.get(get_person_radar_str)
            if has_chinese(get_person_radar_item) or numbers:
                # チャンネル登録者数 6.9万人
                cur = clean_and_convert(get_person_radar_item[:-1])
                print(cur, get_person_radar_item)
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
            global_log.info(self.finish_data["profile_picture_url"])
            download_image_head_url = download_image_file(self.finish_data["profile_picture_url"],
                                                          self.finish_data["user_name"])
            global_log.info(download_image_head_url)
            self.finish_data["profile_picture_url"] = download_image_head_url
            self.page.wait_for_timeout(self.human_wait_time)
            self.page.query_selector('//tp-yt-paper-dialog[@role="dialog"]//div[@id="visibility-button"]').click()
            self.page.wait_for_timeout(self.human_wait_time)
        except Exception:
            global_log.error()
            raise

    def get_10_video_list(self):
        video_contents: List[ElementHandle] = self.page.query_selector_all(
            '//*[@id="primary"]//*[@id="contents"]//ytd-thumbnail[@size="large"]/a')
        for video in video_contents:
            video_url = video.get_attribute("href")
            self.all_urls_list.append("https://www.youtube.com" + video_url)
        for _ in self.all_urls_list[:10]:
            self.urls_list.put(_)
        self.max_len = self.urls_list.qsize()

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
                    headless=headerLess,
                    channel="chrome",
                    args=["--disable-blink-features=AutomationControlled"],
                )
                cur_context = cur_browser.new_context(viewport=return_viewPort(),
                                                      user_agent=user_agent, )

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

                for _ in range(5):
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
                    like_count = get_like_count(page, like_button_view_model.text_content())
                view_info = page.query_selector('//div[@id="info-container"]//yt-formatted-string[@id="info"]')
                if view_info:
                    view_count = get_view_count(view_info.text_content())
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
                        comment_count = get_comment_count(page, commend_info.text_content())
                        break

                if like_count is None \
                        or view_count is None \
                        or comment_count is None:
                    global_log.warning(f"{page_url} --> like_count:{like_count}, "
                                       f"view_count:{view_count}, "
                                       f"comment_count:{comment_count}")

                self.like += like_count if like_count is not None else 0
                self.view += view_count if view_count is not None else 0
                self.comment += comment_count if comment_count is not None else 0
            except Exception:
                raise

    def work(self, _url):
        try:
            if "videos" not in _url:
                _url = _url.removesuffix('/') + "/videos"
            global_log.info(f"youTuBe start --> set {_url} ")
            self.page.goto(_url, wait_until="domcontentloaded")
            self.page.wait_for_timeout(self.human_wait_time)
            errorInfo = self.page.query_selector('//iframe[@src="/error?src=404&ifr=1&error="]')
            if errorInfo:
                raise NotUserData(f"{_url} 用户查询不到")
            get_profile_pic_item = self.page.query_selector('//yt-avatar-shape//img').get_attribute("src")
            self.finish_data["profile_picture_url"] = get_profile_pic_item
            self.get_country_item()
            self.page.wait_for_timeout(self.human_wait_time)
            self.get_10_video_list()
            # 增加并发速 10 -> 稳定
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
                        except RetryableError as re:
                            global_log.error(f"{retry_url} --> RetryableError {str(re)}")
                            # 更换一个
                            self.close_comment_flag = self.close_comment_flag + 1
                            self.urls_list.put(self.all_urls_list[self.close_comment_flag])
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
            self.finish_data["average_likes"] = self.like / self.max_len if self.like != 0 else 0
            self.finish_data["average_views"] = self.view / self.max_len if self.view != 0 else 0
            self.finish_data["average_comments"] = self.comment / self.max_len if self.comment != 0 else 0
            try:
                self.finish_data["average_engagement_rate"] = (
                        (self.finish_data["average_likes"] + self.finish_data["average_comments"])
                        / self.finish_data["average_views"])
            except ZeroDivisionError:
                self.finish_data["average_engagement_rate"] = 0

            self.finish_data["level"] = grade_criteria("youtube", self.finish_data["average_views"])
            inner_CelebrityProfile(self.finish_data)
            self._close_data()
        except Exception:
            global_log.error()
            raise

    def run(self, url):
        global_log.info(f"youTuBe start --> {url}")
        self.work(url)


if __name__ == '__main__':
    with sync_playwright() as playwright:
        # Connect to the running browser instance
        browser = None
        browser_context = playwright.chromium.launch_persistent_context(
            executable_path=executable_path,  # 指定使用谷歌浏览器进行配置
            user_data_dir=rf"C:\chrome-user-data",  # 指定用户数据目录
            headless=False,  # 确保浏览器不是无头模式
            args=["--disable-blink-features=AutomationControlled"]  # 避免自动化检测
        )
        browser_context.add_init_script(
            "const newProto = navigator.__proto__; delete newProto.webdriver; navigator.__proto__ = newProto;"
        )
        Task(browser, browser_context).run('https://www.youtube.com/@thelkfamily/videos')
