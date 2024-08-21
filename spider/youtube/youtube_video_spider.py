"""
@ProjectName: DataAnalysis
@FileName：youtube_video_spider.py
@IDE：PyCharm
@Author：Libre
@Time：2024/8/2 下午4:06
"""
import json
import random
import re
from datetime import datetime
from typing import Optional

from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright, Route

from log.logger import global_log
from spider.sql.data_inner_db import inner_InfluencersVideoProjectData, inner_InfluencersVideoProjectDataByDate
from tool.grading_criteria import convert_words_to_numbers


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

    def _close(self):
        self.response_data = {}
        self.response_sort_data = []
        self.finish_data = {}

    def has_chinese(self, s):
        """检查字符串是否包含任何中文字符"""
        return bool(re.search(r'[\u4e00-\u9fff]', s))

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
                raise ValueError(f"字段替换数字报错 {match_str}")
            return self.clean_and_convert(text[:-1]) * numbers
        else:
            return self.clean_and_convert(text)

    def block_media_requests(self, route: Route, request):
        url = request.url
        if url.endswith('.jpg') or url.endswith('.png') or 'video' in url:
            route.abort()  # 拦截并阻止请求
        else:
            route.continue_()  # 继续其他请求

    def process_page(self):
        """页面处理"""
        feedback = self.page.query_selector('//*[@id="yt-spec-touch-feedback-shape__fill"]')

        if feedback is not None:
            feedback.click()

        self.page.wait_for_timeout(self.human_wait_time)
        user_name = self.page.query_selector(
            '//div[@id="upload-info"]//yt-formatted-string[@id="text"]/a').get_attribute(
            "href")
        self.finish_data["user_name"] = user_name.replace("/", "")

        like_button_view_model = self.page.query_selector(
            '//like-button-view-model//div[@class="yt-spec-button-shape-next__button-text-content"]')
        if like_button_view_model:
            # //like-button-view-model/toggle-button-view-model/button-view-model[@class="yt-spec-button-view-model"]/button
            # aria-label="与另外 433 人一起赞此视频"
            like_count_str = like_button_view_model.text_content()
            if "赞" in like_count_str:
                like_count_str = "0"

            if "12345678901234567890123456789" in like_button_view_model.text_content():
                aria_label = self.page.query_selector(
                    '//like-button-view-model/toggle-button-view-model/button-view-model[@class="yt-spec-button-view-model"]/button').get_attribute(
                    "aria-label")
                like_count_str = aria_label.split(" ")[1]
            like_count = self.extract_number(like_count_str)
            self.finish_data["likes"] = like_count
        view_info = self.page.query_selector('//div[@id="info-container"]//yt-formatted-string[@id="info"]')
        if view_info:
            global_log.info("观看量：" + view_info.text_content())
            view_info_str = view_info.text_content().split(" ")[0]
            view_count = self.extract_number(view_info_str)
            self.finish_data["views"] = view_count

        self.page.click('//tp-yt-paper-button[@id="expand"]')
        self.page.wait_for_timeout(self.human_wait_time)
        cur_date = self.page.query_selector('//yt-formatted-string[@id="info"]/span[3]').text_content().strip()
        releasedTime = self.convert_date(cur_date)
        self.finish_data["releasedTime"] = releasedTime
        self.page.click('//tp-yt-paper-button[@id="collapse"]')
        # 滚动到页面底部
        # while True:
        self.page.wait_for_timeout(self.human_wait_time)
        self.page.mouse.wheel(0, random.randint(300, 500))
        self.page.wait_for_load_state("domcontentloaded")
        for _ in range(5):
            self.page.wait_for_timeout(self.human_wait_time)

            if self.page.query_selector('//*[text()="评论已关闭。"]') is not None:
                self.finish_data["comments"] = 0
                break

            commend_info = self.page.query_selector('//div[@id="leading-section"]//span')
            if commend_info is not None:
                if "评论" in commend_info.text_content():
                    commend_info = self.page.query_selector('//div[@id="leading-section"]//span[2]')
                global_log.info("评论：" + commend_info.text_content())
                comment_count = self.extract_number(commend_info.text_content())
                self.finish_data["comments"] = comment_count
                break

    def convert_date(self, date_str: str) -> str:
        # 定义日期格式列表
        date_formats = [
            '%Y年%m月%d日',  # 格式: 2024年05月28日
            '%b %d, %Y',  # 格式: May 28, 2024
        ]

        # 移除前缀（如果有）
        if date_str.startswith("首播开始于 "):
            date_str = date_str.replace("首播开始于 ", "")

        for date_format in date_formats:
            try:
                # 尝试解析日期字符串
                dt = datetime.strptime(date_str, date_format)
                # 将 datetime 对象格式化为 %Y-%m-%d 格式的字符串
                formatted_date = dt.strftime('%Y-%m-%d')
                return formatted_date
            except ValueError:
                # 如果解析失败，则尝试下一个格式
                continue

        # 如果所有格式都不匹配，则返回原始字符串
        return date_str

    def fetch_page_info(self, _url):
        h5 = self.page.request.get(_url).text()
        match = re.search(r'ytInitialData\s*=\s*({.*?});', h5, re.DOTALL)
        match_str = None
        if match:
            match_str = match.group(1)
        if match_str is None:
            raise ValueError("获取不到ytInitialData")

        h5_json = json.loads(match_str)
        overlay = h5_json.get("overlay")
        reelPlayerOverlayRenderer = overlay.get("reelPlayerOverlayRenderer")
        likeButton = reelPlayerOverlayRenderer.get("likeButton")
        likeButtonRenderer = likeButton.get("likeButtonRenderer")
        likeCount = likeButtonRenderer.get("likeCount") if likeButtonRenderer.get("likeCount") is not None else 0
        self.finish_data["likes"] = likeCount

        reelPlayerHeaderSupportedRenderers = reelPlayerOverlayRenderer.get("reelPlayerHeaderSupportedRenderers")
        reelPlayerHeaderRenderer = reelPlayerHeaderSupportedRenderers.get("reelPlayerHeaderRenderer")
        channelTitleText = reelPlayerHeaderRenderer.get("channelTitleText")
        runs = channelTitleText.get("runs")
        if len(runs) != 1:
            raise ValueError("reelPlayerHeaderRenderer -> runs 获取失败")
        user_name = runs[0].get("text")
        self.finish_data["user_name"] = user_name

        viewCommentsButton = reelPlayerOverlayRenderer.get("viewCommentsButton")
        buttonRenderer = viewCommentsButton.get("buttonRenderer")
        text = buttonRenderer.get("text")
        simpleText = text.get("simpleText")
        comments = self.clean_and_convert(simpleText)
        self.finish_data["comments"] = comments
        engagementPanels = h5_json.get("engagementPanels")
        for engagementPanel in engagementPanels:
            if "structuredDescriptionContentRenderer" in json.dumps(engagementPanel):
                engagementPanelSectionListRenderer = engagementPanel.get("engagementPanelSectionListRenderer")
                content = engagementPanelSectionListRenderer.get("content")
                structuredDescriptionContentRenderer = content.get("structuredDescriptionContentRenderer")
                items = structuredDescriptionContentRenderer.get("items")

                for item in items:
                    if "videoDescriptionHeaderRenderer" in item:
                        videoDescriptionHeaderRenderer = item.get("videoDescriptionHeaderRenderer")
                        publishDate = videoDescriptionHeaderRenderer.get("publishDate")
                        simpleText = publishDate.get("simpleText")
                        releasedTime = self.convert_date(simpleText)
                        self.finish_data["releasedTime"] = releasedTime

                        factoid = videoDescriptionHeaderRenderer.get("factoid")
                        for _ in factoid:
                            if "viewCountFactoidRenderer" in _:
                                viewCountFactoidRenderer = _.get("viewCountFactoidRenderer")
                                factoid_viewCountFactoidRenderer = viewCountFactoidRenderer.get("factoid")
                                factoidRenderer = factoid_viewCountFactoidRenderer.get("factoidRenderer")
                                value = factoidRenderer.get("value")
                                simpleText = value.get("simpleText")
                                views = self.clean_and_convert(simpleText)
                                self.finish_data["views"] = views
                                break
                        break
                break

    def work(self, _url):
        self.page.route('**/*', self.block_media_requests)

        self.page.goto(_url, wait_until="domcontentloaded")
        self.page.wait_for_timeout(self.human_wait_time)
        self.finish_data["platform"] = "youtube"
        self.finish_data["video_url"] = _url
        if "shorts" in _url:
            self.fetch_page_info(_url)
            self.finish_data["type"] = "短视频"
        else:
            self.process_page()
            self.finish_data["type"] = "视频"
        try:
            self.finish_data["engagement_rate"] = (
                    (self.finish_data.get("likes", 0) + self.finish_data.get("comments", 0))
                    / self.finish_data.get("views", 0))
        except Exception:
            self.finish_data["engagement_rate"] = 0

        inner_InfluencersVideoProjectData(self.finish_data)
        inner_InfluencersVideoProjectDataByDate(self.finish_data)
        self._close()

    def run(self, _url):
        # urls = ["https://www.youtube.com/watch?v=rIMehtvFV_A",
        #         "https://www.youtube.com/shorts/3gl_8MOfkrE"]
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
