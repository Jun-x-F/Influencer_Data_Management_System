"""
@ProjectName: Influencer_Data_Management_System
@FileName：public_function.py
@IDE：PyCharm
@Author：Libre
@Time：2024/9/23 下午4:26
"""
from typing import Optional
from urllib.parse import urlparse

from playwright.sync_api import Page, BrowserContext

from log.logger import global_log


def x_cookies(page: Page):
    """获取到指定的cookie"""
    raw_cookies = page.context.cookies()
    _request_cookie = {}
    for cookie in raw_cookies:
        if cookie.get('name') in ["guest_id", "night_mode", "guest_id_marketing", "guest_id_ads", "_twitter_sess",
                                  "external_referer", "kdt", "auth_token", "ct0", "att", "lang", "twid",
                                  "personalization_id"]:
            _request_cookie[cookie.get('name')] = cookie.get('value')

    return _request_cookie


def find_existing_page(context: BrowserContext, domain: str) -> Optional[Page]:
    """
    查找当前上下文中 URL 域名包含指定域名的页面。

    参数：
        domain (str): 要匹配的域名，例如 "x.com"

    返回：
        Page 或 None: 如果找到匹配的页面，返回 Page 对象；否则返回 None。
    """
    for page in context.pages:
        parsed_url = urlparse(page.url)
        if parsed_url.netloc.endswith(domain.lower()):
            global_log.info(f"找到匹配的页面: {page.url}")
            return page
    global_log.info(f"未找到包含 '{domain}' 的页面。")
    return context.new_page()


def create_new_page(page: Page, url: str) -> Page:
    """
    创建一个新的页面并导航到指定的 URL。

    参数：
        url (str): 要导航到的 URL。

    返回：
        Page: 新创建的页面对象。
    """
    try:
        page.goto(url, wait_until="domcontentloaded")
        global_log.info(f"已导航到 {url}")
    except Exception as e:
        global_log.error(f"无法导航到 {url}: {e}")
        page.wait_for_timeout(12000)
    return page
