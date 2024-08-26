"""
@ProjectName: DataAnalysis
@FileName：run_spider.py
@IDE：PyCharm
@Author：Libre
@Time：2024/8/5 下午1:46
"""
import datetime
import json

from playwright.sync_api import sync_playwright

from log.logger import global_log
from spider.config.config import headerLess, return_viewPort, user_agent, redis_conn, message_queue
from spider.ins import ins_spider
from spider.ins.ins_post_feel_spider import ins_videos_start_spider
from spider.tiktok import tiktok_spider
from spider.tiktok import tiktok_video_spider
from spider.youtube import youtube_spider
from spider.youtube import youtube_video_spider
from tool.get_ws import get_ws_id


@global_log.log_exceptions
def setup_browser(context, ws_id=None):
    """设置浏览器上下文，添加反爬虫脚本"""
    if ws_id is not None:
        browser = context.chromium.connect_over_cdp(ws_id)
        browser_context = browser.contexts[0]
    else:
        browser = context.chromium.launch(
            headless=headerLess,
            channel="chrome",
            args=["--disable-blink-features=AutomationControlled"]
        )
        browser_context = browser.new_context(
            viewport=return_viewPort(),
            user_agent=user_agent
        )
    browser_context.add_init_script(
        "const newProto = navigator.__proto__; delete newProto.webdriver; navigator.__proto__ = newProto;"
    )
    return browser, browser_context


@global_log.log_exceptions
def run_task(spider_class, url, ws_id=None):
    """运行指定的爬虫任务"""
    with sync_playwright() as playwright:
        browser, context = setup_browser(playwright, ws_id)
        spider_class.Task(browser, context).run(url)


@global_log.log_exceptions
def work(url: str, cur: dict, flag, _id) -> int:
    platform = "YouTube" if "youtube" in url else "TikTok" if "tiktok" in url else "Instagram" if "instagram" in url else None
    if not platform:
        message_queue.add(_id, "链接无法解析...")
        return 404

    is_influencer_task = flag == 1
    spider_map = {
        "YouTube": (youtube_spider if is_influencer_task else youtube_video_spider),
        "TikTok": (tiktok_spider if is_influencer_task else tiktok_video_spider),
        "Instagram": (ins_spider if is_influencer_task else "ins_post_feel_spider"),
    }

    spider_class = spider_map[platform]
    task_type = "红人信息" if is_influencer_task else "视频信息"

    message_queue.add(_id,
                      f"后台判断为获取{platform} {task_type}的任务，开始解析浏览器ws_id" if is_influencer_task else f"后台判断为获取{platform} {task_type}的任务，开始执行任务")

    ws_id = get_ws_id() if is_influencer_task else None
    if ws_id:
        message_queue.add(_id, f"解析浏览器ws_id为{ws_id}，开始执行任务")
    global_log.info(f"平台{platform} {task_type}任务开始执行，url为{url}，ws_id为{ws_id}")
    if spider_class == "ins_post_feel_spider":
        ins_videos_start_spider(url)
    else:
        run_task(spider_class, url, ws_id)
    return 200


def run_spider(url: str, cur: dict, flag: int, _id: str) -> dict:
    message_queue.add(_id, f"接收到任务链接: {url}, 开始解析url")
    message = {}
    try:
        code = work(url, cur, flag, _id)
        if code == 200:
            message["code"] = 200
            message["message"] = "抓取成功"
        else:
            message["code"] = code
            message["message"] = "链接解析失败"
    except Exception as e:
        global_log.error(f"{url} 异常: {e}")
        message["code"] = 500
        message["message"] = "网络异常, 检查日志"
        cur["error_time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        redis_conn.set_value(url, json.dumps(cur))
    message_queue.add(_id,
                      f"任务链接: {url} 执行结果为 {message.get('message')}",
                      status="error" if message.get("code") == 500 else "doing")
    return message

#
# if __name__ == '__main__':
#     run_spider()
