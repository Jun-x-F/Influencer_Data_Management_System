"""
@ProjectName: Influencer_Data_Management_System
@FileName：x_influencer.py
@IDE：PyCharm
@Author：Libre
@Time：2024/9/23 下午5:09
"""
import json
import os
import re
from urllib.parse import urlparse

import requests
from playwright.sync_api import Response, sync_playwright, Browser, BrowserContext

from log.logger import global_log
from spider.config.config import redis_conn
from spider.sql.data_inner_db import inner_InfluencersVideoProjectData, inner_InfluencersVideoProjectDataByDate
from spider.x.public_function import x_cookies, find_existing_page
from tool.FileUtils import get_project_path
from tool.JsonUtils import dfs_get_all_values_by_path_extended
from tool.TimeUtils import TimeUtils


class Task:
    def __init__(self, _browser: Browser, _context: BrowserContext):
        self.browser = _browser
        self.context = _context
        self.page, isNewPage = find_existing_page(self.context, "x.com")
        if isNewPage:
            try:
                self.page = context.new_page()
                self.page.goto("https://x.com/home", wait_until="domcontentloaded")
            except Exception as e:
                self.page.wait_for_timeout(12000)
        self.response_data = {
            "platform": "x",

        }
        file_dir = os.path.join(get_project_path(), r"spider\x\city_zh_en.json")
        # 读取映射表
        with open(file_dir, 'r', encoding='utf-8') as f:
            self.city_zh_en = json.load(f)
        # redis 读取 x_headers和x_cookies
        self.headers = {}
        self.cookies = {}
        x_headers_str = redis_conn.get_value("x_headers")
        x_cookies_str = redis_conn.get_value("x_cookies")

        if x_headers_str is not None:
            self.headers = json.loads(x_headers_str)
        if x_cookies_str is not None:
            self.cookies = json.loads(x_cookies_str)

    def get_post_info(self, focalTweetId):
        """获取贴子信息"""
        params = {
            'variables': '{"focalTweetId":"1837947053928075349","with_rux_injections":false,"rankingMode":"Relevance","includePromotedContent":true,"withCommunity":true,"withQuickPromoteEligibilityTweetFields":true,"withBirdwatchNotes":true,"withVoice":true}',
            'features': '{"rweb_tipjar_consumption_enabled":true,"responsive_web_graphql_exclude_directive_enabled":true,"verified_phone_label_enabled":false,"creator_subscriptions_tweet_preview_api_enabled":true,"responsive_web_graphql_timeline_navigation_enabled":true,"responsive_web_graphql_skip_user_profile_image_extensions_enabled":false,"communities_web_enable_tweet_community_results_fetch":true,"c9s_tweet_anatomy_moderator_badge_enabled":true,"articles_preview_enabled":true,"responsive_web_edit_tweet_api_enabled":true,"graphql_is_translatable_rweb_tweet_is_translatable_enabled":true,"view_counts_everywhere_api_enabled":true,"longform_notetweets_consumption_enabled":true,"responsive_web_twitter_article_tweet_consumption_enabled":true,"tweet_awards_web_tipping_enabled":false,"creator_subscriptions_quote_tweet_preview_enabled":false,"freedom_of_speech_not_reach_fetch_enabled":true,"standardized_nudges_misinfo":true,"tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled":true,"rweb_video_timestamps_enabled":true,"longform_notetweets_rich_text_read_enabled":true,"longform_notetweets_inline_media_enabled":true,"responsive_web_enhance_cards_enabled":false}',
            'fieldToggles': '{"withArticleRichContentState":true,"withArticlePlainText":false,"withGrokAnalyze":false,"withDisallowedReplyControls":false}',
        }

        variables_str = params.get("variables")
        raw_variables = json.loads(variables_str)
        raw_variables["focalTweetId"] = focalTweetId
        variables_str = json.dumps(raw_variables)
        params["variables"] = variables_str

        response = requests.get(
            'https://x.com/i/api/graphql/QuBlQ6SxNAQCt6-kBiCXCQ/TweetDetail',
            params=params,
            cookies=self.cookies,
            headers=self.headers,
        )
        raw_json = response.json()
        data = raw_json.get("data")
        threaded_conversation_with_injections_v2 = data.get("threaded_conversation_with_injections_v2")
        instructions = threaded_conversation_with_injections_v2.get("instructions")
        for instruction in instructions:
            _type = instruction.get("type")
            if _type != "TimelineAddEntries":
                continue
            entries = instruction.get("entries")
            for entry in entries:
                entryId = entry.get("entryId")
                if entryId != f"tweet-{focalTweetId}":
                    global_log.info("x --> 这是一条评论，跳过！！！")
                # 红人名称
                self.response_data["user_name"] = dfs_get_all_values_by_path_extended(raw_json,
                                                                                      ["content", "itemContent",
                                                                                       "tweet_results", "result",
                                                                                       "core",
                                                                                       "user_results", "result",
                                                                                       "legacy", "screen_name"]
                                                                                      )[0]
                # 红人全称
                self.response_data["full_name"] = dfs_get_all_values_by_path_extended(raw_json,
                                                                                      ["content", "itemContent",
                                                                                       "tweet_results", "result",
                                                                                       "core",
                                                                                       "user_results", "result",
                                                                                       "legacy", "name"]
                                                                                      )[0]
                # 观看量
                self.response_data["views"] = dfs_get_all_values_by_path_extended(raw_json,
                                                                                  ["content", "itemContent",
                                                                                   "tweet_results", "result",
                                                                                   "views",
                                                                                   "count"]
                                                                                  )[0]
                # 收藏
                self.response_data["collections"] = dfs_get_all_values_by_path_extended(raw_json,
                                                                                        ["content", "itemContent",
                                                                                         "tweet_results", "result",
                                                                                         "legacy",
                                                                                         "bookmark_count"]
                                                                                        )[0]
                # 点赞
                self.response_data["likes"] = dfs_get_all_values_by_path_extended(raw_json,
                                                                                  ["content", "itemContent",
                                                                                   "tweet_results", "result",
                                                                                   "legacy",
                                                                                   "favorite_count"]
                                                                                  )[0]

                # 评论
                self.response_data["comments"] = dfs_get_all_values_by_path_extended(raw_json,
                                                                                     ["content", "itemContent",
                                                                                      "tweet_results", "result",
                                                                                      "legacy",
                                                                                      "reply_count"]
                                                                                     )[0]
                # 获取类型
                media_type = dfs_get_all_values_by_path_extended(raw_json,
                                                                 ["content", "itemContent",
                                                                  "tweet_results", "result",
                                                                  "legacy",
                                                                  "entities", "media", "type"]
                                                                 )[0]
                if media_type == "video":
                    self.response_data["type"] = "视频"
                else:
                    self.response_data["type"] = "图片"

                # 参与率
                self.response_data["engagement_rate"] = (
                        (int(self.response_data["comments"]) + int(self.response_data["likes"]))
                        / int(self.response_data["views"])
                )

                # 创建时间
                original_time = dfs_get_all_values_by_path_extended(raw_json,
                                                                    ["content", "itemContent",
                                                                     "tweet_results", "result",
                                                                     "legacy",
                                                                     "created_at"]
                                                                    )[0]
                # 发布时间
                target_timezone = "Asia/Shanghai"  # 中国标准时间
                converted_time = TimeUtils.convert_time(original_time, target_timezone)
                if converted_time is None:
                    raise ValueError(f"x --> TimeUtils.convert_time --> converted_time is None, {original_time}")
                self.response_data["releasedTime"] = converted_time

    def extract_status_id(self, url):
        """
        从给定的 X.com（原 Twitter）状态 URL 中提取状态 ID。

        参数：
            url (str): 状态的完整 URL，例如 'https://x.com/webflite/status/1837947053928075349'

        返回：
            str: 提取到的状态 ID，例如 '1837947053928075349'
            如果无法提取，则返回 None
        """
        try:
            # 解析 URL
            parsed_url = urlparse(url)
            path = parsed_url.path  # 获取路径部分，例如 '/webflite/status/1837947053928075349'

            # 使用正则表达式匹配状态 ID
            match = re.search(r'/status/(\d+)', path)
            if match:
                status_id = match.group(1)
                return status_id
            else:
                print("无法从 URL 中提取状态 ID。请确保 URL 格式正确。")
                return None
        except Exception as e:
            print(f"发生错误: {e}")
            return None

    def handle_request(self, response: Response):
        """监听url并且获取到指定的headers"""
        if self.headers != {}:
            return
        headers = response.request.headers
        if ("authorization" in headers.__str__()
                and "x-csrf-token" in headers.__str__()
                and "x-client-uuid" in headers.__str__()
                and "x-client-transaction-id" in headers.__str__()):
            self.headers = headers
            # 有效期1天
            redis_conn.set_value("x_headers", json.dumps(headers), 24 * 3600)

    def work(self, url):
        self.response_data["video_url"] = url
        focalTweetId = self.extract_status_id(url)
        if focalTweetId is None:
            raise ValueError(f"x --> extract_status_id -->extract_status_id {focalTweetId}")
        self.get_post_info(focalTweetId)
        inner_InfluencersVideoProjectData(self.response_data)
        inner_InfluencersVideoProjectDataByDate(self.response_data)

    def run(self, url):
        """启动器"""
        if self.headers == {}:
            self.page.on('response', self.handle_request)
            if self.page.url != "x.com":
                self.page.goto("https://x.com/home", wait_until="domcontentloaded")
            else:
                self.page.reload(wait_until="domcontentloaded")
            self.page.wait_for_timeout(1200)
        if self.cookies == {}:
            self.cookies = x_cookies(self.page)
            # 有效期30天
            redis_conn.set_value("x_cookies", json.dumps(self.cookies), 30 * 24 * 3600)
        self.work(url)
        global_log.info(self.response_data)


if __name__ == '__main__':
    with sync_playwright() as playwright:
        browser = playwright.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0]
        page = None
        for _page in context.pages:
            if "x.com" in _page.url:
                page = _page
                break
        if page is None:
            page = context.new_page()

        Task(browser, context).run("https://x.com/TheRabbitHole84/status/1837900702527770697")
