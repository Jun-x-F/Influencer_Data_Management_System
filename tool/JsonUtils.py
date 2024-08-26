"""
@ProjectName: Influencer_Data_Management_System
@FileName：JsonUtils.py
@IDE：PyCharm
@Author：Libre
@Time：2024/8/23 上午11:31
"""


def dfs_get_value(json_data, _key, cur_parent=None, parent=None):
    """
    解析json -> 根据key进行解析 -> 如果存在有指定位置要求，使用parent传递上一级json的key
        @:param json_data 需要解析的数据
        @:param _key 关键key
        @:param 递归前上一层的parent
        @:param 指定的parent
    """
    if isinstance(json_data, dict):
        for key, item in json_data.items():
            if key == _key:
                if parent is not None:
                    if cur_parent == parent:
                        return item
                else:
                    return item
            res = dfs_get_value(item, _key, key, parent)
            if res is not None:
                return res
    elif isinstance(json_data, list):
        for item in json_data:
            if isinstance(item, str):
                continue
            res = dfs_get_value(item, _key, cur_parent, parent)
            if res is not None:
                return res
    return None
