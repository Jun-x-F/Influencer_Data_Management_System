"""
@ProjectName: DataAnalysis
@FileName：ga4_request_constructor.py
@IDE：PyCharm
@Author：Libre
@Time：2024/7/24 下午4:08
"""
from google.analytics.data_v1beta import Dimension, Metric, DateRange


def construct_dimensions(data):
    ls = []
    for item in data:
        ls.append(Dimension(name=item))
    return ls


def construct_metric(data):
    ls = []
    for item in data:
        ls.append(Metric(name=item))
    return ls


def construct_dateRange(start, end):
    return [DateRange(start_date=start, end_date=end)]


if __name__ == '__main__':
    print(type(construct_metric(["1", "2", "3", "4"])))
    print(construct_dimensions(["1", "2", "3", "4"]))
    print(construct_dateRange("1", "2"))
