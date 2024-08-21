"""
@ProjectName: Influencer_Data_Management_System
@FileName：FileUtils.py
@IDE：PyCharm
@Author：Libre
@Time：2024/8/21 上午10:37
"""
import os
from pathlib import Path
from typing import AnyStr


def get_project_path() -> AnyStr:
    """获取项目地址"""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def build_tree_for_py_files(path: Path, level=0):
    tree = {}

    for child in path.iterdir():
        if child.is_dir():
            sub_tree = build_tree_for_py_files(child, level + 1)
            # 仅当子目录中包含 .py 文件时，才添加到树中
            if sub_tree:
                tree[child.name] = sub_tree
        elif child.suffix == '.py' and child.name != '__init__.py':
            tree[child.name] = level  # 文件的层级

    # 如果当前目录中没有 .py 文件，也没有包含 .py 文件的子目录，则返回空
    return tree if tree else None
