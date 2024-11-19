"""
提供给ins进行列表查询
@ProjectName: DataAnalysis
@FileName：ins_spider.py
@IDE：PyCharm
@Author：Libre
@Time：2024/7/23 下午4:41
"""
import json
import random
from typing import Optional

from playwright.sync_api import Page, sync_playwright, BrowserContext, Browser, Request, Response

from log.logger import global_log
from spider.config.config import redis_conn, ins_account, headerLess


class Task:
    def __init__(self, _browser: Optional[Browser], _context: BrowserContext, page: Page):
        self.code = None
        self.url = None
        self.browser: Optional[Browser] = _browser
        self.context = _context
        self.page: Optional[Page] = page
        self.human_wait_time = 6000
        self.response_data = {}
        self.response_sort_data = []
        self.finish_data = {}
        self.request_body = {}
        self.isFinished = False

    @global_log.log_exceptions
    def _get_user_info(self, response: Response):
        if self.isFinished is True:
            return
        url = response.url
        if url == "https://www.instagram.com/graphql/query":
            # 获取响应内容
            url_request: Request = response.request
            url_request_json = url_request.post_data_json
            fb_api_req_friendly_name = url_request_json.get("fb_api_req_friendly_name")
            # 切换成帖子
            # PolarisProfileReelsTabContentQuery
            # PolarisProfileReelsTabContentQuery_connection
            # if fb_api_req_friendly_name in ["PolarisProfilePostsTabContentDirectQuery_connection",
            #                                 "PolarisProfilePostsDirectQuery"]:
            if fb_api_req_friendly_name in ["PolarisProfileReelsTabContentQuery_connection",
                                            "PolarisProfileReelsTabContentQuery",
                                            "PolarisProfilePostsQuery",
                                            "PolarisProfilePostsTabContentQuery_connection"]:

                body = response.json()
                data = body.get("data")

                if fb_api_req_friendly_name == "PolarisProfilePostsQuery" or fb_api_req_friendly_name == "PolarisProfilePostsTabContentQuery_connection":
                    xdt_api__v1__feed__user_timeline_graphql_connection = data.get(
                        "xdt_api__v1__feed__user_timeline_graphql_connection"
                    )
                    edges = xdt_api__v1__feed__user_timeline_graphql_connection.get("edges")
                    for edge in edges:
                        node = edge.get("node")
                        # 将数据进行缓存
                        cur_code = node.get("code")
                        redis_conn.set_value(node.get("code"), json.dumps(node), 12 * 3600)
                        if cur_code == self.code:
                            self.response_data[cur_code] = node
                            self.isFinished = True
                            break
                else:

                    xdt_api__v1__clips__user__connection_v2 = data.get(
                        "xdt_api__v1__clips__user__connection_v2")
                    edges = xdt_api__v1__clips__user__connection_v2.get("edges")
                    for edge in edges:
                        node = edge.get("node")
                        media = node.get("media")
                        # 将数据进行缓存
                        cur_code = media.get("code")
                        redis_conn.set_value(media.get("code"), json.dumps(media), 12 * 3600)
                        if cur_code == self.code:
                            self.response_data[cur_code] = media
                            self.isFinished = True
                            break

    def scroll_to_bottom(self):
        # 滚动到页面底部
        self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

    def work(self):
        self.page.on('response', self._get_user_info)
        # self.page.wait_for_timeout(self.human_wait_time)
        self.page.goto(self.url, wait_until="domcontentloaded")
        self.page.wait_for_timeout(12000)

        for _ in range(30):
            if self.isFinished:
                return
            self.scroll_to_bottom()
            # 每6秒
            self.page.wait_for_timeout(random.randint(3000, 6000))

    def run(self, url, code):
        # if self.page is None or self.page.query_selector('//input[@name="username"]'):
        #     self._login()
        self.url = url
        self.code = code
        self.work()
        return self.response_data


def get_ins_info(fileDir, url, code, cur_cookies):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch_persistent_context(
            user_data_dir=fileDir,  # 指定用户数据目录
            headless=headerLess,  # 确保浏览器不是无头模式
            args=["--disable-blink-features=AutomationControlled"]  # 避免自动化检测
        )
        # get_ins_info_browser = playwright.chromium.connect_over_cdp(ws_id)
        # get_ins_info_context = get_ins_info_browser.contexts[0]

        cookies_str = redis_conn.get_value(cur_cookies)
        if cookies_str is not None:
            _cookies = json.loads(cookies_str)
            browser.add_cookies(_cookies)
        browser.add_init_script(
            "const newProto = navigator.__proto__; delete newProto.webdriver; navigator.__proto__ = newProto;"
        )
        get_ins_info_page = browser.new_page()
        return Task(None, browser, get_ins_info_page).run(url=url, code=code)


def to_int(ls: list) -> list:
    """转int"""
    cur_ = []
    for i in ls:
        if i is None:
            cur_.append(0)
        else:
            cur_.append(int(i))
    return cur_


def save_cookies(page, key):
    # 获取当前页面上下文的 cookies
    cookies = page.context.cookies()
    cookies_str = json.dumps(cookies)

    redis_conn.set_value(key, cookies_str, 30 * 24 * 3600)


def random_account_():
    ial = len(ins_account)
    return ins_account[random.randint(0, ial - 1)]


if __name__ == '__main__':
    print(random_account_())
