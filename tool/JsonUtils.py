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


def dfs_get_all_values_by_path_extended(json_data, path):
    """
    通过指定的路径按顺序遍历 JSON 数据并收集所有对应的值。
    路径中的元素可以是字符串（字典键）或整数（列表索引）。
    如果某些层级缺失路径中的键或索引，则继续在该层级下的子节点中搜索剩余路径。

    @param json_data: 需要解析的 JSON 数据（字典或列表）
    @param path: 一个按顺序排列的键和索引列表，表示遍历路径
    @return: 一个包含所有匹配值的列表；如果没有匹配，返回空列表
    """
    results = []

    def dfs(node, path_index):
        if path_index == len(path):
            results.append(node)
            return

        if isinstance(node, dict):
            current_key = path[path_index]
            if isinstance(current_key, str) and current_key in node:
                dfs(node[current_key], path_index + 1)
            # 继续在子节点中搜索剩余路径
            for key, value in node.items():
                dfs(value, path_index)
        elif isinstance(node, list):
            current_key = path[path_index]
            if isinstance(current_key, int):
                if 0 <= current_key < len(node):
                    dfs(node[current_key], path_index + 1)
            # 在所有列表项中继续搜索剩余路径
            for item in node:
                dfs(item, path_index)
        # 其他类型无法继续搜索

    dfs(json_data, 0)
    return results