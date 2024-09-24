"""
@ProjectName: DataAnalysis
@FileName：ins_spider.py
@IDE：PyCharm
@Author：Libre
@Time：2024/7/23 下午4:41
"""
import json
import random
import re
import time
from typing import Optional

from playwright.sync_api import Page, sync_playwright, BrowserContext, Browser, Request, Response

from log.logger import global_log
from spider.config.config import headerLess, return_viewPort, user_agent, ins_cookies
from spider.sql.data_inner_db import inner_CelebrityProfile
from tool.JsonUtils import dfs_get_all_values_by_path_extended
from tool.download_file import download_image_file
from tool.grading_criteria import grade_criteria
from tool.ins_code import get_deOne_code


class Task:
    def __init__(self, _browser: Browser, _context: BrowserContext, page: Page):
        self.browser = _browser
        self.context = _context
        self.page: Optional[Page] = page
        self.account = "wagwanalbs"
        self.password = "Nokia1202$$"
        self.human_wait_time = 6000
        self.response_data = {}
        self.response_sort_data = []
        self.finish_data = {}

    def _close_data(self):
        self.response_data = {}
        self.response_sort_data = []
        self.finish_data = {}

    def _login(self):
        if (self.page is None or
                ("accounts/login" in self.page.url and "two_factor" not in self.page.url)):
            if self.page is None:
                self.page = self.context.new_page()
            global_log.info("ins任务 开始登录...")
            self.page.goto("https://www.instagram.com/accounts/login/", wait_until="domcontentloaded")
            try:
                self.page.wait_for_timeout(self.human_wait_time)
                self.page.wait_for_selector('//input[@name="username"]').fill(self.account)
                self.page.wait_for_timeout(self.human_wait_time / 3)
                self.page.wait_for_selector('//input[@name="password"]').fill(self.password)
                self.page.wait_for_timeout(self.human_wait_time / 3)
                self.page.click('//button[@type="submit"]')
            except Exception:
                global_log.info("ins任务 存在登录...")
        else:
            global_log.info("ins任务 页面存在...")
        self.page.wait_for_timeout(self.human_wait_time)
        self._check_login()

    def _check_login(self):
        if "two_factor" in self.page.url:
            get_safe_code = get_deOne_code()
            self.page.wait_for_selector('//input[@name="verificationCode"]').fill(get_safe_code)
            self.page.wait_for_timeout(self.human_wait_time)
            self.page.click('//button[@type="button"]')

        # //button[text()="保存信息"]
        for _ in range(5):
            if "onetap" in self.page.url and self.page.query_selector('//*[@aria-label="Instagram"]'):
                global_log.info("登录成功...")
                break
            self.page.wait_for_timeout(self.human_wait_time)

        save_browser_info = self.page.query_selector('//button[text()="保存信息"]')
        if save_browser_info:
            save_browser_info.click()

        self.page.wait_for_timeout(self.human_wait_time)

        open_message_item = self.page.query_selector('//button[text()="以后再说"]')
        if open_message_item:
            open_message_item.click()

        # login/two_factor? --> 输入验证码
        # challenge --> 判断用户是否登录
        # 一天接口请求1k次
        # //*[text()="以wagwanalbs的身份继续"]
        ...

    def extract_username(self, url: str) -> Optional[str]:
        # 使用正则表达式匹配用户名部分
        match = re.search(r'https://www\.instagram\.com/([^/]+)/?', url)
        if match:
            return match.group(1)
        return None

    @global_log.log_exceptions
    def _get_user_info(self, response: Response):
        url = response.url
        if url == "https://www.instagram.com/graphql/query":
            # 获取响应内容
            url_request: Request = response.request
            url_request_json = url_request.post_data_json
            fb_api_req_friendly_name = url_request_json.get("fb_api_req_friendly_name")
            # "PolarisProfilePageContentDirectQuery" --> 红人数据
            # "PolarisProfileReelsTabContentQuery_connection" --> 滚动生成10条视频
            # "PolarisProfileReelsTabContentQuery" --> 前10条视频
            # "PolarisUserHoverCardContentV2DirectQuery" --> 获取单条视频url的用户详情, 进行二次匹配
            if fb_api_req_friendly_name in ["PolarisProfilePageContentQuery",
                                            "PolarisProfileReelsTabContentQuery",
                                            "PolarisProfileReelsTabContentQuery_connection"]:
                body = response.json()
                cur_data = self.response_data.get(fb_api_req_friendly_name, [])
                cur_data.append(body)
                self.response_data[fb_api_req_friendly_name] = cur_data

    def work(self, _url):
        user_name = self.extract_username(_url)
        self.finish_data["user_name"] = user_name
        self.finish_data["platform"] = "instagram"
        self.finish_data["index_url"] = _url
        self.page.on('response', self._get_user_info)
        if "reels" not in _url:
            _url = _url.strip().removesuffix('/') + "/reels"
        print(_url)
        self.page.goto(_url, wait_until="domcontentloaded")
        self.page.wait_for_timeout(self.human_wait_time)
        # 获取国家信息
        self.page.wait_for_selector(f'//h2/*[text()="{user_name}"]').click()
        self.page.wait_for_timeout(self.human_wait_time / 2)
        region = self.page.wait_for_selector('//span[text()="帐户所在地"]/following-sibling::span[1]').text_content()
        self.page.wait_for_selector('//button[text()="关闭"]').click()
        self.page.wait_for_timeout(self.human_wait_time / 2)
        self.finish_data["region"] = region

        isFinish = False
        self.page.mouse.wheel(0, 1000)
        for _ in range(30):
            if len(self.response_data) == 2:
                isFinish = True
                break
            time.sleep(random.randint(1, 3))

        if isFinish is False:
            raise ValueError("获取self.response_data 报错")
        for key, values in self.response_data.items():
            global_log.info(f"ins -->reponse.name  {key}")
            if key == "PolarisProfilePageContentQuery":
                # 姓名
                cur_full_name_ls = dfs_get_all_values_by_path_extended(values, ["data", "full_name"])
                self.finish_data["full_name"] = cur_full_name_ls[0]
                # 粉丝数
                cur_fans_ls = dfs_get_all_values_by_path_extended(values, ["data", "follower_count"])
                self.finish_data["follower_count"] = cur_fans_ls[0]
                # 缓存照片
                cur_ptc_ls = dfs_get_all_values_by_path_extended(values, ["data", "profile_pic_url"])
                # 下载照片
                cur_url = download_image_file(cur_ptc_ls[0], self.finish_data["user_name"])
                self.finish_data["profile_picture_url"] = cur_url
                # pk
                cur_pk_ls = dfs_get_all_values_by_path_extended(values, ["data", "user", "pk"])
                self.finish_data["user_id"] = cur_pk_ls[0]
            else:
                # 播放量
                cur_play_ls = dfs_get_all_values_by_path_extended(values, ["xdt_api__v1__clips__user__connection_v2",
                                                                           "edges", "node", "media", "play_count"
                                                                           ])
                avg_play_count = sum(cur_play_ls)/len(cur_play_ls)
                # 评论数
                cur_comment_ls = dfs_get_all_values_by_path_extended(values, ["xdt_api__v1__clips__user__connection_v2",
                                                                              "edges", "node", "media", "comment_count"
                                                                              ])
                avg_comment_count = sum(cur_comment_ls) / len(cur_comment_ls)
                # 点赞
                like_comment_ls = dfs_get_all_values_by_path_extended(values, ["xdt_api__v1__clips__user__connection_v2",
                                                                               "edges", "node", "media", "like_count"
                                                                               ])
                avg_like_count = sum(like_comment_ls) / len(like_comment_ls)
                self.finish_data["average_likes"] = avg_like_count
                self.finish_data["average_comments"] = avg_comment_count
                self.finish_data["average_views"] = avg_play_count


        self.finish_data["level"] = grade_criteria(self.finish_data["platform"], self.finish_data["average_views"])
        self.finish_data["average_engagement_rate"] = \
            ((self.finish_data["average_likes"] + self.finish_data["average_comments"])
             / self.finish_data["average_views"])
        global_log.info(
            f"ins -->self.finish_data  {self.finish_data}")
        inner_CelebrityProfile(self.finish_data, isById=True)
        self._close_data()
        self.page.wait_for_timeout(self.human_wait_time)

    def save_cookies(self, file_path):
        # 获取当前页面上下文的 cookies
        cookies = self.page.context.cookies()

        # 将 cookies 保存为 JSON 文件
        with open(file_path, 'w') as file:
            json.dump(cookies, file)

    def run(self, url):
        if self.page is None or self.page.query_selector('//input[@name="username"]'):
            self._login()
        global_log.info("进入ins页面")
        self.page.wait_for_timeout(6000)
        self.save_cookies("ins_cookies.json")
        self.work(url)


def ins_start_spider(url):
    """新的启动器"""
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
        Task(ins_videos_browser, ins_videos_context, ins_videos_page).work(url)
        time.sleep(5)
