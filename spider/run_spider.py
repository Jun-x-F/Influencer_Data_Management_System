"""
@ProjectName: DataAnalysis
@FileName：run_spider.py
@IDE：PyCharm
@Author：Libre
@Time：2024/8/5 下午1:46
"""
import datetime
import json
import re
import time

from playwright.sync_api import sync_playwright

from log.logger import global_log
from spider.config.config import headerLess, return_viewPort, user_agent, redis_conn, message_queue, executable_path
from spider.ins import ins_spider
from spider.ins.ins_post_feel_spider import ins_videos_start_spider
from spider.ins.ins_spider import ins_start_spider
from spider.template.notFoundData import NotUserData
from spider.tiktok import tiktok_spider
from spider.tiktok import tiktok_video_spider
from spider.x import x_celerity, x_influencer
from spider.youtube import youtube_spider
from spider.youtube import youtube_video_spider


@global_log.log_exceptions
def run_task(spider_class, url, is_launch_persistent_context: bool):
    print(is_launch_persistent_context)
    """运行指定的爬虫任务"""
    with sync_playwright() as playwright:
        """设置浏览器上下文，添加反爬虫脚本"""
        if is_launch_persistent_context:
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
                headless=headerLess,  # 确保浏览器不是无头模式
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
        else:
            browser = playwright.chromium.launch(
                env={
                    "LANG": "zh_CN.UTF-8",
                    "LC_ALL": "zh_CN.UTF-8",
                },
                headless=headerLess,
                channel="chrome",
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
            browser_context = browser.new_context(
                viewport=return_viewPort(),
                user_agent=user_agent,
                extra_http_headers={
                    "Accept-Language": "zh-CN,zh;q=0.9",
                },
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
        try:
            spider_class.Task(browser, browser_context).run(url)
        except Exception as e:
            global_log.error()
            raise
        finally:
            browser_context.close()
            if browser:
                browser.close()


def get_platform(url):
    """
    根据 URL 判断平台名称。

    参数：
        url (str): 要判断的平台 URL。

    返回：
        str 或 None: 对应的平台名称，若未匹配则返回 None。
    """
    # 定义平台的正则表达式模式及其对应的名称
    platform_patterns = {
        re.compile(r'youtube.com', re.IGNORECASE): "YouTube",
        re.compile(r'youtu.be', re.IGNORECASE): "YouTube",
        re.compile(r'tiktok.com', re.IGNORECASE): "TikTok",
        re.compile(r'instagram.com', re.IGNORECASE): "Instagram",
        re.compile(r'x.com', re.IGNORECASE): "X",
        re.compile(r'twitter.com', re.IGNORECASE): "X"
    }

    # 遍历字典，检查是否有模式匹配 URL
    for pattern, platform_name in platform_patterns.items():
        if pattern.search(url):
            return platform_name

    # 如果没有匹配，返回 None
    return None


@global_log.log_exceptions
def work(url: str, cur: dict, flag, _id, times) -> int:
    platform = get_platform(url)
    if not platform:
        message_queue.add(_id, "链接无法解析...")
        return 404

    is_influencer_task = flag == 1
    spider_map = {
        "YouTube": (youtube_spider if is_influencer_task else youtube_video_spider),
        "TikTok": (tiktok_spider if is_influencer_task else tiktok_video_spider),
        "Instagram": (ins_spider if is_influencer_task else ins_videos_start_spider),
        "X": (x_celerity if is_influencer_task else x_influencer)
    }

    spider_class = spider_map[platform]
    task_type = "红人信息" if is_influencer_task else "视频信息"
    if times > 0:
        message_queue.add(_id, f"重试...")
    else:
        message_queue.add(_id, f"后台判断为获取{platform} {task_type}的任务，开始执行任务")

    # ws_id = get_ws_id() if (is_influencer_task or platform in ["YouTube", "X"]) else None
    # if ws_id:
    #     message_queue.add(_id, f"解析浏览器ws_id为{ws_id}，开始执行任务")
    global_log.info(f"平台 {platform} {task_type}任务开始执行，url为{url}, spider_class {spider_class}")
    if spider_class == ins_videos_start_spider:
        ins_videos_start_spider(url)
    elif spider_class == ins_spider:
        global_log.info("进入新的ins红人启动器")
        ins_start_spider(url)
    elif spider_class == youtube_spider:
        global_log.info("进入新的Youtube红人启动器")
        youtube_spider.run_youtube_spider(url=url)
    elif spider_class == youtube_video_spider:
        global_log.info("进入新的Youtube视频启动器")
        youtube_video_spider.youtube_video_spider(url=url)
    else:
        run_task(spider_class, url, platform in ["YouTube", "X"])
    return 200


def run_spider(url: str, cur: dict, flag: int, _id: str) -> dict:
    message_queue.add(_id, f"接收到任务链接: {url}, 开始解析url")
    message = {}
    isFinish = False
    for item in range(3):
        try:
            code = work(url, cur, flag, _id, item)
            if code == 200:
                message["code"] = 200
                message["message"] = "平台数据 抓取成功"
            else:
                message["code"] = code
                message["message"] = f"链接 {url} \n格式错误，重新检查..."
            isFinish = True
            break
        except NotUserData as nud:
            # 如果是这个异常的话，直接跳出循环

            message["code"] = 404
            message["message"] = str(nud)
            isFinish = True
            break
        except Exception as e:
            global_log.error(f"{url} 异常: {e}")
        finally:
            time.sleep(1)

    if isFinish is False:
        message["code"] = 500
        if _id != "schedule_test":
            message["message"] = "网络异常, 检查日志，稍后重试..."
        else:
            message["message"] = f"{url}"
        cur["error_time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        redis_conn.set_value(url, json.dumps(cur))

    return message


if __name__ == "__main__":
    url = "https://youtu.be/pFVqtVJgk-U?si=FOL94ZI7DY3bhMb2&t=145"
    platform = get_platform(url)
    print(platform)  # 输出: X
