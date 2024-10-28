"""
@ProjectName: DataAnalysis
@FileName：grading_criteria.py
@IDE：PyCharm
@Author：Libre
@Time：2024/7/29 下午4:48
"""


def grade_criteria(platform: str, data: int) -> str:
    """
    :param platform: 平台
    :param data: 平均播放量
    :return:
    """
    if platform == "youtube":
        if data >= 1000000:
            return 'S'
        elif data >= 500000:
            return 'A'
        elif data >= 200000:
            return 'B'
        elif data >= 50000:
            return 'C'
        elif data >= 10000:
            return 'D'
        elif data > 0:
            return 'P'
        else:
            return ''
    elif platform == "tiktok" or platform == "instagram":
        if data >= 3000000:
            return 'S'
        elif data >= 1000000:
            return 'A'
        elif data >= 500000:
            return 'B'
        elif data >= 200000:
            return 'C'
        elif data >= 100000:
            return 'D'
        elif data > 0:
            return 'P'
        else:
            return ''


# Convert words to numbers
convert_words_to_numbers = {
    "万": 10000,
    "m": 10000,
    "M": 10000,
    "k": 1000,
    "K": 1000,
    "千": 1000,

}
