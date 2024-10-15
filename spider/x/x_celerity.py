"""
@ProjectName: Influencer_Data_Management_System
@FileName：x_celerity.py
@IDE：PyCharm
@Author：Libre
@Time：2024/9/23 上午10:56
"""
import json
import os.path
from urllib.parse import urlparse

import requests
from playwright.sync_api import sync_playwright, Response, Browser, BrowserContext

from log.logger import global_log
from spider.config.config import redis_conn
from spider.sql.data_inner_db import inner_CelebrityProfile
from spider.x.public_function import x_cookies, find_existing_page
from tool.FileUtils import get_project_path
from tool.JsonUtils import dfs_get_all_values_by_path_extended
from tool.download_file import download_image_file


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

    def get_post_info(self):
        url = "https://x.com/i/api/graphql/E3opETHurmVJflFsUBVuUQ/UserTweets"
        params = {
            "variables": "{\"userId\":\"44196397\",\"count\":20,\"includePromotedContent\":true,\"withQuickPromoteEligibilityTweetFields\":true,\"withVoice\":true,\"withV2Timeline\":true}",
            "features": "{\"rweb_tipjar_consumption_enabled\":true,\"responsive_web_graphql_exclude_directive_enabled\":true,\"verified_phone_label_enabled\":false,\"creator_subscriptions_tweet_preview_api_enabled\":true,\"responsive_web_graphql_timeline_navigation_enabled\":true,\"responsive_web_graphql_skip_user_profile_image_extensions_enabled\":false,\"communities_web_enable_tweet_community_results_fetch\":true,\"c9s_tweet_anatomy_moderator_badge_enabled\":true,\"articles_preview_enabled\":true,\"responsive_web_edit_tweet_api_enabled\":true,\"graphql_is_translatable_rweb_tweet_is_translatable_enabled\":true,\"view_counts_everywhere_api_enabled\":true,\"longform_notetweets_consumption_enabled\":true,\"responsive_web_twitter_article_tweet_consumption_enabled\":true,\"tweet_awards_web_tipping_enabled\":false,\"creator_subscriptions_quote_tweet_preview_enabled\":false,\"freedom_of_speech_not_reach_fetch_enabled\":true,\"standardized_nudges_misinfo\":true,\"tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled\":true,\"rweb_video_timestamps_enabled\":true,\"longform_notetweets_rich_text_read_enabled\":true,\"longform_notetweets_inline_media_enabled\":true,\"responsive_web_enhance_cards_enabled\":false}",
            "fieldToggles": "{\"withArticlePlainText\":false}"
        }

        variables_str = params.get("variables")
        variables_json = json.loads(variables_str)
        variables_json["userId"] = self.response_data.get("user_id")
        params["variables"] = json.dumps(variables_json)

        response = requests.get(url, headers=self.headers, cookies=self.cookies, params=params)

        raw_json = response.json()
        raw_data = raw_json.get("data")
        raw_user = raw_data.get("user")
        result = raw_user.get("result")
        timeline_v2 = result.get("timeline_v2")
        timeline = timeline_v2.get("timeline")
        instructions = timeline.get("instructions")
        like_ls = []
        comments_ls = []
        views_ls = []
        for instruction in instructions:
            _type = instruction.get("type")

            if _type == "TimelinePinEntry":
                global_log.info("x --> 开始解析置顶数据")
                # 观看量
                views_ls.extend(dfs_get_all_values_by_path_extended(instruction,
                                                                    ["type", "entry", "content", "itemContent",
                                                                     "tweet_results",
                                                                     "result",
                                                                     "views", "count"]))
                # 回复数量
                comments_ls.extend(dfs_get_all_values_by_path_extended(instruction,
                                                                       ["type", "entry", "content", "itemContent",
                                                                        "tweet_results",
                                                                        "result",
                                                                        "legacy", "reply_count"]))

                # 点赞数量
                like_ls.extend(dfs_get_all_values_by_path_extended(instruction,
                                                                   ["type", "entry", "content", "itemContent",
                                                                    "tweet_results",
                                                                    "result",
                                                                    "legacy", "favorite_count"]))

            elif _type == "TimelineAddEntries":
                global_log.info("x --> 开始解析前20条帖子")
                entries = instruction.get("entries")
                for entry in entries:
                    if "quoted_status_result" in json.dumps(entry):
                        global_log.info("x --> 这是一个引用回复的帖子")
                    elif "retweeted_status_result" in json.dumps(entry):
                        global_log.info("x --> 这是一个转发回复的帖子, 跳过！！！")
                        continue
                    else:
                        global_log.info("x --> 这是一个正常帖子")
                    # 观看量
                    views_ls.extend(
                        dfs_get_all_values_by_path_extended(entry, ["content", "itemContent", "tweet_results", "result",
                                                                    "views", "count"]))
                    # 点赞
                    like_ls.extend(
                        dfs_get_all_values_by_path_extended(entry, ["content", "itemContent", "tweet_results", "result",
                                                                    "legacy", "favorite_count"]))
                    # 回复
                    comments_ls.extend(
                        dfs_get_all_values_by_path_extended(entry, ["content", "itemContent", "tweet_results", "result",
                                                                    "legacy", "reply_count"]))

        views_ls = self.to_int(views_ls)
        like_ls = self.to_int(like_ls)
        comments_ls = self.to_int(comments_ls)

        self.response_data["average_views"] = sum(views_ls) / len(views_ls)
        self.response_data["average_likes"] = sum(like_ls) / len(like_ls)
        self.response_data["average_comments"] = sum(comments_ls) / len(comments_ls)
        self.response_data["average_engagement_rate"] = (sum(like_ls) + sum(comments_ls)) / sum(views_ls)

    def to_int(self, ls: list) -> list:
        """转int"""
        cur_ = []
        for i in ls:
            cur_.append(int(i))
        return cur_

    def get_user_info(self, user_name):
        """获取用户信息"""
        url = "https://x.com/i/api/graphql/Yka-W8dz7RaEuQNkroPkYw/UserByScreenName"
        params = {
            "variables": "{\"screen_name\":\"elonmusk\",\"withSafetyModeUserFields\":true}",
            "features": "{\"hidden_profile_subscriptions_enabled\":true,\"rweb_tipjar_consumption_enabled\":true,"
                        "\"responsive_web_graphql_exclude_directive_enabled\":true,\"verified_phone_label_enabled\":false,"
                        "\"subscriptions_verification_info_is_identity_verified_enabled\":true,"
                        "\"subscriptions_verification_info_verified_since_enabled\":true,"
                        "\"highlights_tweets_tab_ui_enabled\":true,\"responsive_web_twitter_article_notes_tab_enabled\":true,"
                        "\"subscriptions_feature_can_gift_premium\":true,"
                        "\"creator_subscriptions_tweet_preview_api_enabled\":true,"
                        "\"responsive_web_graphql_skip_user_profile_image_extensions_enabled\":false,"
                        "\"responsive_web_graphql_timeline_navigation_enabled\":true}",
            "fieldToggles": "{\"withAuxiliaryUserLabels\":false}"
        }
        variables_str = params.get("variables")
        variables_json = json.loads(variables_str)
        variables_json["screen_name"] = user_name
        params["variables"] = json.dumps(variables_json)

        response = requests.get(url, headers=self.headers, cookies=self.cookies, params=params)

        raw_json = response.json()
        # 获取rest_id
        self.response_data["user_id"] = raw_json.get("data").get("user").get("result").get("rest_id")
        self.response_data["follower_count"] = \
            dfs_get_all_values_by_path_extended(raw_json, ["data", "user", "legacy", "followers_count"])[0]
        self.response_data["user_name"] = user_name
        self.response_data["full_name"] = \
            dfs_get_all_values_by_path_extended(raw_json, ["data", "user", "legacy", "name"])[0]
        self.response_data["profile_picture_url"] = download_image_file(
            dfs_get_all_values_by_path_extended(raw_json, ["data", "user", "legacy", "profile_image_url_https"])[0],
            user_name)
        en_city_ls = dfs_get_all_values_by_path_extended(raw_json, ["data", "user", "legacy", "location"])
        global_log.info(f"x --> 地区查询结果，{en_city_ls}")
        en_city_ = en_city_ls[0]
        if en_city_ != '':
            for _ in self.city_zh_en:
                if en_city_.lower() == _.get("en").lower():
                    self.response_data["region"] = _.get("cn")
                    break

    def get_username_by_url(self, raw_url):
        """获取用户的网络名称"""
        # 提取用户名
        parsed_url = urlparse(raw_url)
        path = parsed_url.path.strip('/')
        username = path.split('/')[0]  # 假设用户名在第一个路径段

        if not username:
            global_log.error(f"x --> {raw_url} 无法从 URL 中提取用户名。")
            raise ValueError("x --> get_username_by_url --> {raw_url} 无法从 URL 中提取用户名。")
        return username

    def work(self, url):
        global_log.info(f"x --> {url}")
        self.response_data["index_url"] = url
        user_name = self.get_username_by_url(url)
        global_log.info(f"X --> 获取红人视频，解析出来的姓名是{user_name}")
        self.get_user_info(user_name)
        self.get_post_info()
        inner_CelebrityProfile(self.response_data, isById=True)

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

        Task(page).run("https://x.com/__silent_")
