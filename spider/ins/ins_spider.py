"""
@ProjectName: DataAnalysis
@FileName：ins_spider.py
@IDE：PyCharm
@Author：Libre
@Time：2024/7/23 下午4:41
"""
import random
import re
from typing import Optional, Union

from playwright.sync_api import Page, sync_playwright, BrowserContext, Browser, Request, Response

from log.logger import global_log
from spider.sql.data_inner_db import inner_CelebrityProfile
from tool.download_file import download_image_file
from tool.grading_criteria import grade_criteria
from tool.ins_code import get_deOne_code


class Task:
    def __init__(self, _browser: Browser, _context: BrowserContext):
        self.browser = _browser
        self.context = _context
        self.page: Optional[Page] = None
        for page in self.context.pages:
            if "instagram" in page.url:
                self.page = page
                break
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
            if fb_api_req_friendly_name in ["PolarisProfilePageContentDirectQuery",
                                            "PolarisProfileReelsTabContentQuery"]:
                body = response.json()
                cur_data = self.response_data.get(fb_api_req_friendly_name, [])
                cur_data.append(body)
                self.response_data[fb_api_req_friendly_name] = cur_data

    def _fetch_polarisProfilePageContentDirectQuery_data(self) -> None:
        PolarisProfilePageContentDirectQuery_Json = self.response_data.get("PolarisProfilePageContentDirectQuery")
        for item in PolarisProfilePageContentDirectQuery_Json:
            PolarisProfilePageContentDirectQuery_data = item.get("data")
            PolarisProfilePageContentDirectQuery_user_data = PolarisProfilePageContentDirectQuery_data.get("user")
            city_name = PolarisProfilePageContentDirectQuery_user_data.get("city_name", None)
            full_name = PolarisProfilePageContentDirectQuery_user_data.get("full_name", None)
            profile_pic_url = PolarisProfilePageContentDirectQuery_user_data.get("profile_pic_url", None)
            follower_count = PolarisProfilePageContentDirectQuery_user_data.get("follower_count", None)
            user_id = PolarisProfilePageContentDirectQuery_user_data.get("id", None)
            self.finish_data["user_id"] = user_id
            # self.finish_data["city"] = city_name
            self.finish_data["full_name"] = full_name
            download_image_head_url = download_image_file(profile_pic_url,
                                                          self.finish_data["user_name"])
            global_log.info(download_image_head_url)
            self.finish_data["profile_picture_url"] = download_image_head_url
            self.finish_data["follower_count"] = follower_count

    def _fetch_same_info(self, param: str) -> None:
        PolarisProfilePostsDirectQuery_Json = self.response_data.get(param)
        for item in PolarisProfilePostsDirectQuery_Json:
            data = item.get("data")
            xdt_api__v1__clips__user__connection_v2 = data.get(
                "xdt_api__v1__clips__user__connection_v2")
            edges = xdt_api__v1__clips__user__connection_v2.get("edges")

            for edge in edges:
                node = edge.get("node")
                media = node.get("media")
                like_count = media.get("like_count")
                comment_count = media.get("comment_count")
                play_count = media.get("play_count")
                self.response_sort_data.append({
                    "like_count": like_count,
                    "comment_count": comment_count,
                    "play_count": play_count
                })

    @global_log.log_exceptions
    def _calculate_average(self) -> tuple[Union[float, int], Union[float, int], Union[float, int]]:
        recent_10_data = self.response_sort_data[:10]
        # 提取所有字段的值
        like_counts = [item['like_count'] for item in recent_10_data if item['like_count'] is not None]
        comment_counts = [item['comment_count'] for item in recent_10_data if item['comment_count'] is not None]
        taken_ats = [item['play_count'] for item in recent_10_data if item['play_count'] is not None]

        # 计算平均值
        avg_like_count = sum(like_counts) / len(like_counts) if like_counts else 0
        avg_comment_count = sum(comment_counts) / len(comment_counts) if comment_counts else 0
        avg_play_count = sum(taken_ats) / len(taken_ats) if taken_ats else 0

        return avg_like_count, avg_comment_count, avg_play_count


    def work(self, _url):
        user_name = self.extract_username(_url)
        self.finish_data["user_name"] = user_name
        self.finish_data["platform"] = "instagram"
        self.finish_data["index_url"] = _url
        self.page.on('response', self._get_user_info)
        if "reels" not in _url:
            _url = _url.removesuffix('/') + "/reels"
        self.page.goto(_url, wait_until="domcontentloaded")
        self.page.wait_for_timeout(self.human_wait_time)
        # 获取国家信息
        self.page.wait_for_selector(f'//h2/*[text()="{user_name}"]').click()
        self.page.wait_for_timeout(self.human_wait_time/2)
        region = self.page.wait_for_selector('//span[text()="帐户所在地"]/following-sibling::span[1]').text_content()
        self.page.wait_for_selector('//button[text()="关闭"]').click()
        self.page.wait_for_timeout(self.human_wait_time / 2)
        self.finish_data["region"] = region

        self.page.mouse.wheel(0, random.randint(100, 1000))
        while True:
            if len(self.response_data) == 2:
                break

        self._fetch_polarisProfilePageContentDirectQuery_data()
        self._fetch_same_info("PolarisProfileReelsTabContentQuery")

        # self.response_sort_data.sort(key=lambda x: x["taken_at"], reverse=True)

        avg_like_count, avg_comment_count, avg_play_count = self._calculate_average()

        self.finish_data["average_likes"] = avg_like_count
        self.finish_data["average_comments"] = avg_comment_count
        self.finish_data["average_views"] = avg_play_count
        self.finish_data["level"] = grade_criteria(self.finish_data["platform"], self.finish_data["average_views"])
        self.finish_data["average_engagement_rate"] = \
            ((self.finish_data["average_likes"] + self.finish_data["average_comments"])
             / self.finish_data["average_views"])

        inner_CelebrityProfile(self.finish_data, isById=True)
        self._close_data()
        self.page.wait_for_timeout(self.human_wait_time)

        # account_name = self.extract_username(_url)
        # if account_name:
        #     account_name_src = self.page.wait_for_selector(f'img[@alt="{account_name}的头像"]').get_attribute("src")
        # https://scontent-nrt1-2.cdninstagram.com/v/t51.2885-19/418140547_1016600006095323_5211962420708439817_n.jpg?stp=dst-jpg_s150x150\u0026_nc_ht=scontent-nrt1-2.cdninstagram.com\u0026_nc_cat=1\u0026_nc_ohc=jXhMDiivcaYQ7kNvgGXgVfH\u0026edm=APHcPcMBAAAA\u0026ccb=7-5\u0026oh=00_AYB7iEQpOc_C5y4Q4UE2YuqAwKIgtOrhCLCI6E0sUXqJ6g\u0026oe=66A683EA\u0026_nc_sid=bef7bc
        # https://scontent-nrt1-2.cdninstagram.com/v/t51.2885-19/418140547_1016600006095323_5211962420708439817_n.jpg?stp=dst-jpg_s150x150&_nc_ht=scontent-nrt1-2.cdninstagram.com&_nc_cat=1&_nc_ohc=jXhMDiivcaYQ7kNvgGXgVfH&edm=AFg4Q8wBAAAA&ccb=7-5&oh=00_AYC4EoqHtR0BwntqPi4eHD-jDcDY_ZdKiDHbhPJuchIJ7A&oe=66A683EA&_nc_sid=0b30b7"
        # https://scontent-nrt1-2.cdninstagram.com/v/t51.2885-19/418140547_1016600006095323_5211962420708439817_n.jpg?_nc_ht=scontent-nrt1-2.cdninstagram.com\u0026_nc_cat=1\u0026_nc_ohc=jXhMDiivcaYQ7kNvgGXgVfH\u0026edm=APHcPcMBAAAA\u0026ccb=7-5\u0026oh=00_AYBIb8tPiKJiITrWXhXsaRrI3QYKzhoj21qT6zG-Y01PAQ\u0026oe=66A683EA\u0026_nc_sid=bef7bc
        # 等待页面加载完毕
        # 拿到姓名，头像，粉丝数，国家，平台，近10个视频的播放量，参与率，点赞数，评论数，
        # 保留红人信息，地址信息，标签信息

    def run(self, url):
        if self.page is None or self.page.query_selector('//input[@name="username"]'):
            self._login()
        self.work(url)
        # https://www.instagram.com/gem0816/
        # https://www.instagram.com/reel/C9rcLz8vFkI/


if __name__ == '__main__':
    with sync_playwright() as playwright:
        # Connect to the running browser instance
        browser = playwright.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0]
        Task(browser, context).run()
