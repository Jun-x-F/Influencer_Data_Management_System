"""
@ProjectName: DataAnalysis
@FileName：xlsx.py
@IDE：PyCharm
@Author：Libre
@Time：2024/7/16 上午11:45
"""
import os
from datetime import datetime


def find_xlsx_files_by_fileName(directory, file_name):
    # 获取今天的日期
    today = datetime.today()
    # 格式化日期为 YYYYMMDD
    today_str = today.strftime('%Y-%m-%d')

    # 获取目录中的所有文件
    files = os.listdir(directory)

    # 匹配今天日期的 .xlsx 文件，允许模糊查询
    matched_files = [rf"{directory}\{f}" for f in files if f.endswith('.xlsx') and today_str in f and file_name in f]

    return matched_files


def find_xlsx_files_by_directory(directory):
    # 获取今天的日期
    today = datetime.today()
    # 格式化日期为 YYYYMMDD
    today_str = today.strftime('%Y-%m-%d')

    # 获取目录中的所有文件
    files = os.listdir(directory)

    # 匹配今天日期的 .xlsx 文件，允许模糊查询
    matched_files = [rf"{directory}\{f}" for f in files if f.endswith('.xlsx') and today_str in f]

    return matched_files
