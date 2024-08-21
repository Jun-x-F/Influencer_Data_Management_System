"""
@ProjectName: DataAnalysis
@FileName：run_spider.py
@IDE：PyCharm
@Author：Libre
@Time：2024/8/5 下午1:46
"""
import datetime
import json
from typing import Optional

from playwright.sync_api import sync_playwright

from log.logger import global_log
from spider.config.config import headerLess, return_viewPort, user_agent, redis_conn
from spider.ins import ins_post_feel_spider
from spider.ins import ins_spider
from spider.spider_notice import spider_notice_to_celebrity, spider_notice_to_influencersVideo, Notice
from spider.tiktok import tiktok_spider
from spider.tiktok import tiktok_video_spider
from spider.youtube import youtube_spider
from spider.youtube import youtube_video_spider
from tool.get_ws import get_ws_id

spider_notice: Optional[Notice] = None


@global_log.log_exceptions
def work(url: str, cur: dict, flag, _id) -> int:
    if "youtube" in url:
        if flag == 1:
            spider_notice.add_notice(_id, "判断为获取YouTube红人信息，开始解析浏览器ws_id")
            ws = get_ws_id()
            global_log.info(ws)
            spider_notice.add_notice(_id, f"浏览器ws_id为{ws}，开始执行任务")
            with sync_playwright() as playwright:
                browser = playwright.chromium.connect_over_cdp(ws)
                context = browser.contexts[0]
                context.add_init_script(
                    "const newProto = navigator.__proto__; delete newProto.webdriver; navigator.__proto__ = newProto;"
                )
                youtube_spider.Task(browser, context).run(url)
        else:
            spider_notice.add_notice(_id, "判断为获取YouTube视频信息，开始执行任务")
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(
                    headless=headerLess,
                    channel="chrome",
                    args=["--disable-blink-features=AutomationControlled"]
                )
                context = browser.new_context(viewport=return_viewPort(),
                                              user_agent=user_agent, )
                context.add_init_script(
                    "const newProto = navigator.__proto__; delete newProto.webdriver; navigator.__proto__ = newProto;"
                )
                youtube_video_spider.Task(browser, context).run(url)
    elif "tiktok" in url:
        if flag == 1:
            spider_notice.add_notice(_id, "判断为获取TikTok红人信息，开始解析浏览器ws_id")
            ws = get_ws_id()
            global_log.info(ws)
            spider_notice.add_notice(_id, f"浏览器ws_id为{ws}，开始执行任务")
            with sync_playwright() as playwright:
                browser = playwright.chromium.connect_over_cdp(ws)
                context = browser.contexts[0]
                context.add_init_script(
                    "const newProto = navigator.__proto__; delete newProto.webdriver; navigator.__proto__ = newProto;"
                )
                tiktok_spider.Task(browser, context).run(url)
        else:
            spider_notice.add_notice(_id, "判断为获取TikTok视频信息，开始执行任务")
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(
                    headless=headerLess,
                    channel="chrome",
                    args=["--disable-blink-features=AutomationControlled"]
                )
                context = browser.new_context(viewport=return_viewPort(),
                                              user_agent=user_agent, )
                context.add_init_script(
                    "const newProto = navigator.__proto__; delete newProto.webdriver; navigator.__proto__ = newProto;"
                )
                tiktok_video_spider.Task(browser, context).run(url)
    elif "instagram" in url:
        if flag == 1:
            spider_notice.add_notice(_id, "判断为获取Instagram红人信息，开始解析浏览器ws_id")
            ws = get_ws_id()
            global_log.info(ws)
            spider_notice.add_notice(_id, f"浏览器ws_id为{ws}，开始执行任务")
            with sync_playwright() as playwright:
                browser = playwright.chromium.connect_over_cdp(ws)
                global_log.info(browser)
                context = browser.contexts[0]
                context.add_init_script(
                    "const newProto = navigator.__proto__; delete newProto.webdriver; navigator.__proto__ = newProto;"
                )
                ins_spider.Task(browser, context).run(url)
        else:
            spider_notice.add_notice(_id, "判断为获取Instagram视频信息，开始执行任务")
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(
                    headless=headerLess,
                    channel="chrome",
                    args=["--disable-blink-features=AutomationControlled"]
                )
                context = browser.new_context(viewport=return_viewPort(),
                                              user_agent=user_agent, )
                context.add_init_script(
                    "const newProto = navigator.__proto__; delete newProto.webdriver; navigator.__proto__ = newProto;"
                )
                ins_post_feel_spider.Task(browser, context).run(url)
    else:
        spider_notice.add_notice(_id, "链接无法解析...")
        return 404
    return 200


def run_spider(url: str, cur: dict, flag: int, _id: str) -> dict:
    global spider_notice
    spider_notice = (spider_notice_to_celebrity
                     if flag == 1
                     else spider_notice_to_influencersVideo)

    spider_notice.add_notice(_id, f"接收到链接为{url}, 开始解析url")
    message = {}
    try:
        code = work(url, cur, flag, _id)
        if code == 200:
            message["code"] = 200
            message["message"] = "成功"
        else:
            message["code"] = code
            message["message"] = "链接解析失败"
    except Exception as e:
        global_log.error(f"{url} 异常: {e}")
        message["code"] = 500
        message["message"] = "爬虫异常, 检查日志"
        cur["error_time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        redis_conn.set_value(url, json.dumps(cur))
    spider_notice.add_notice(_id, f"链接{url} 执行结果为 {message.get('message')}")
    return message

#
# if __name__ == '__main__':
#     run_spider()
