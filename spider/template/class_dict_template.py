"""
@ProjectName: Influencer_Data_Management_System
@FileName：class_dict_template.py
@IDE：PyCharm
@Author：Libre
@Time：2024/8/9 下午2:09
"""
from collections import deque


class FIFODict:
    """先进先出的dict"""
    def __init__(self):
        self._data = {}
        self._keys = deque()

    def enqueue(self, key, value):
        if key not in self._data:
            self._keys.append(key)  # 添加键到队列的末尾
        self._data[key] = value  # 添加键值对到字典

    def dequeue(self):
        if not self._keys:
            raise KeyError("Dequeue from an empty FIFO queue")
        key = self._keys.popleft()  # 从队列的开头弹出最早插入的键
        return key, self._data.pop(key)  # 删除字典中的对应键值对并返回

    def is_empty(self):
        """判断队列是否为空"""
        return len(self._keys) == 0

    def __contains__(self, key):
        return key in self._data

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self.enqueue(key, value)

    def __delitem__(self, key):
        if key in self._data:
            self._keys.remove(key)  # 从队列中移除键
            del self._data[key]  # 从字典中移除键值对

    def __len__(self):
        return len(self._data)

    def __repr__(self):
        return f"{self.__class__.__name__}({list(self._keys)}, {self._data})"

    def get(self, key, default=None):
        """获取键的值，如果键不存在，则返回默认值"""
        return self._data.get(key, default)

    def total_size(self):
        """获取所有值的大小之和"""
        return sum(len(value) for value in self._data.values())

    def items(self):
        """返回队列中的所有键值对"""
        return ((key, self._data[key]) for key in self._keys)  # 返回生成器

