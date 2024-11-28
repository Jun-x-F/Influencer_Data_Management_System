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
from typing import Optional

from dateutil.parser import parse
from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright, Route

from log.logger import global_log
from spider.config.config import executable_path, return_viewPort, user_agent
from spider.sql.data_inner_db import inner_InfluencersVideoProjectData, inner_InfluencersVideoProjectDataByDate
from spider.youtube.youtube_public_func import get_like_count, get_view_count, get_comment_count
from tool.JsonUtils import dfs_get_all_values_by_path_extended


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
            self.page = self.context.new_page()
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
        # 添加全称
        self.finish_data["full_name"] = self.page.query_selector(
            '//div[@id="upload-info"]//yt-formatted-string[@id="text"]').text_content().strip()

        like_button_view_model = self.page.query_selector(
            '//like-button-view-model//div[@class="yt-spec-button-shape-next__button-text-content"]')
        if like_button_view_model:
            like_count = get_like_count(self.page, like_button_view_model.text_content())
            self.finish_data["likes"] = like_count
        view_info = self.page.query_selector('//div[@id="info-container"]//yt-formatted-string[@id="info"]')
        if view_info:
            view_count = get_view_count(view_info.text_content())
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
                comment_count = get_comment_count(self.page, commend_info.text_content())
                self.finish_data["comments"] = comment_count
                break

    def convert_date(self, date_str: str) -> Optional[str]:
        try:
            # 使用 dateutil.parser 尝试解析整个日期字符串
            parsed_date = parse(date_str, fuzzy=True, dayfirst=True)
            # 返回标准格式的日期字符串 'YYYY-MM-DD'
            return parsed_date.strftime("%Y-%m-%d")
        except ValueError:
            # 如果解析失败，返回 None
            return None
        # # 定义日期格式列表
        # date_formats = [
        #     '%Y年%m月%d日',  # 格式: 2024年05月28日
        #     '%b %d, %Y',  # 格式: May 28, 2024
        #     '%Y/%m/%d',
        # ]
        #
        # # 使用正则表达式提取可能的日期部分，例如：2024/09/19、2024-09-19 等
        # date_match = re.search(r"\d{4}[-/]\d{2}[-/]\d{2}", date_str)
        #
        # if date_match:
        #     # 提取出匹配的日期字符串部分
        #     date_str = date_match.group()
        #
        # # 移除前缀（如果有）
        # if date_str.startswith("首播开始于 "):
        #     date_str = date_str.replace("首播开始于 ", "")
        #
        # for date_format in date_formats:
        #     try:
        #         # 尝试解析日期字符串
        #         dt = datetime.strptime(date_str, date_format)
        #         # 将 datetime 对象格式化为 %Y-%m-%d 格式的字符串
        #         formatted_date = dt.strftime('%Y-%m-%d')
        #         return formatted_date
        #     except ValueError:
        #         # 如果解析失败，则尝试下一个格式
        #         continue
        #
        # # 如果所有格式都不匹配，则返回原始字符串
        # return date_str

    def fetch_page_info(self, _url):
        h5 = self.page.request.get(_url).text()
        match = re.search(r'ytInitialData\s*=\s*({.*?});', h5, re.DOTALL)
        match_str = None
        if match:
            match_str = match.group(1)
        if match_str is None:
            raise ValueError("获取不到ytInitialData")

        h5_json = json.loads(match_str)
        # engagementPanels -> engagementPanelSectionListRenderer -> structuredDescriptionContentRenderer -> items ->
        # videoDescriptionHeaderRenderer -> channel -> simpleText
        full_name_list = dfs_get_all_values_by_path_extended(h5_json,
                                                             ["engagementPanels", "engagementPanelSectionListRenderer",
                                                              "structuredDescriptionContentRenderer", "items",
                                                              "videoDescriptionHeaderRenderer",
                                                              "channel", "simpleText"])
        if len(full_name_list) == 0:
            raise ValueError("youtube -> 查询不到full name --> h5_json -> dfs_get_all_values_by_path_extended")
        self.finish_data["full_name"] = full_name_list[0]

        overlay = h5_json.get("overlay")
        reelPlayerOverlayRenderer = overlay.get("reelPlayerOverlayRenderer")
        likeButton = reelPlayerOverlayRenderer.get("likeButton")
        likeButtonRenderer = likeButton.get("likeButtonRenderer")
        likeCount = likeButtonRenderer.get("likeCount") if likeButtonRenderer.get("likeCount") is not None else 0
        self.finish_data["likes"] = likeCount
        # print(reelPlayerOverlayRenderer)
        reelPlayerHeaderSupportedRenderers = reelPlayerOverlayRenderer.get("reelPlayerHeaderSupportedRenderers")
        reelPlayerHeaderRenderer = reelPlayerHeaderSupportedRenderers.get("reelPlayerHeaderRenderer")
        channelTitleText = reelPlayerHeaderRenderer.get("channelTitleText")
        # print("channelTitleText", channelTitleText)
        if channelTitleText is not None:
            runs = channelTitleText.get("runs")
            if len(runs) != 1:
                raise ValueError("reelPlayerHeaderRenderer -> runs 获取失败")
            user_name = runs[0].get("text")
            self.finish_data["user_name"] = user_name
        else:
            metapanel = reelPlayerOverlayRenderer.get("metapanel")
            reelMetapanelViewModel = metapanel.get("reelMetapanelViewModel")
            metadataItems = reelMetapanelViewModel.get("metadataItems")
            for item in metadataItems:
                if "reelChannelBarViewModel" in item:
                    reelChannelBarViewModel = item.get("reelChannelBarViewModel")
                    channelName = reelChannelBarViewModel.get("channelName")
                    self.finish_data["user_name"] = channelName.get("content")
        try:
            viewCommentsButton = reelPlayerOverlayRenderer.get("viewCommentsButton")
            buttonRenderer = viewCommentsButton.get("buttonRenderer")
            text = buttonRenderer.get("text")
            simpleText = text.get("simpleText")
            comments = self.clean_and_convert(simpleText)
        except Exception:
            comments = 0
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
        self.page.wait_for_timeout(self.human_wait_time * 2)
        truth_url = self.page.url
        global_log.info(f"youtube video -->{_url} --> {truth_url}")
        self.finish_data["platform"] = "youtube"
        self.finish_data["video_url"] = _url
        if "shorts" in truth_url:
            self.fetch_page_info(truth_url)
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
    # ws = get_ws_id()
    # print(ws)
    with sync_playwright() as playwright:
        browser = None
        browser_context = playwright.chromium.launch_persistent_context(
            env={
                "LANG": "zh_CN.UTF-8",
                "LC_ALL": "zh_CN.UTF-8",
            },
            extra_http_headers={
                "Accept-Language": "zh-CN,zh;q=0.9",
            },
            executable_path=executable_path,  # 指定使用谷歌浏览器进行配置
            user_data_dir=rf"C:\chrome-user-data",  # 指定用户数据目录
            headless=False,  # 确保浏览器不是无头模式
            viewport=return_viewPort(),
            user_agent=user_agent,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
                "--enable-automation=false",
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-gpu",
                "--disable-software-rasterizer",
            ]
        )
        browser_context.add_init_script(
            """
                const newProto = navigator.__proto__; delete newProto.webdriver; navigator.__proto__ = newProto;"
                 Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                 Object.defineProperty(navigator, 'languages', { get: () => ['zh-CN', 'zh'] });
                 Object.defineProperty(navigator, 'language', { get: () => 'zh-CN' });
                 Object.defineProperty(navigator, 'platform', { get: () => 'Win32' });
                 Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
           """
        )
        # https://www.youtube.com/watch?v=YEoihc-EI3o
        Task(None, browser_context).run("https://www.youtube.com/shorts/lwCsuPR5aC0")
        browser_context.close()
        # playwright.stop()
