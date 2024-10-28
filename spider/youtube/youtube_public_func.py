"""
@ProjectName: Influencer_Data_Management_System
@FileName：youtube_public_func.py
@IDE：PyCharm
@Author：Libre
@Time：2024/8/26 下午4:22
"""
import re
from typing import Optional

from playwright.sync_api import Page

from log.logger import global_log
from tool.grading_criteria import convert_words_to_numbers


def clean_and_convert(s):
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


def has_chinese(s):
    """检查字符串是否包含任何中文字符"""
    return bool(re.search(r'[\u4e00-\u9fff]', s))


def extract_number(text) -> Optional[float]:
    """提取并转换字符串中的数字"""
    match_str = text[-1]
    numbers = convert_words_to_numbers.get(match_str)  # 默认为 1 如果未找到
    global_log.info(f"extract_number --> {text, numbers}")
    if has_chinese(text) or numbers is not None:
        return clean_and_convert(text[:-1]) * numbers
    else:
        return clean_and_convert(text)


def get_like_count(page: Page, data_str):
    global_log.info("点赞：" + data_str)
    # //like-button-view-model/toggle-button-view-model/button-view-model[@class="yt-spec-button-view-model"]/button
    # aria-label="与另外 433 人一起赞此视频"
    like_count_str = data_str
    if "赞" in like_count_str:
        like_count_str = "0"

    if "12345678901234567890123456789" in like_count_str or "this" in like_count_str:
        aria_label = page.query_selector(
            '//like-button-view-model/toggle-button-view-model/button-view-model['
            '@class="yt-spec-button-view-model"]/button').get_attribute(
            "aria-label")
        like_count_str = aria_label.split(" ")[1]
    global_log.info(f"点赞的str -> {like_count_str}")
    like_count = extract_number(like_count_str)
    return like_count


def get_view_count(data_str):
    global_log.info("观看量：" + data_str)
    view_info_str = data_str.replace("次观看", "").split(" ")[0]
    view_count = extract_number(view_info_str)
    return view_count


def get_comment_count(page: Page, data_str):
    if "评论" in data_str:
        commend_info = page.query_selector('//div[@id="leading-section"]//span[2]').text_content()
    else:
        commend_info = data_str
    global_log.info("评论：" + commend_info)
    comment_count = extract_number(commend_info)
    return comment_count
