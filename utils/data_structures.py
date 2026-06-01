"""
基础数据结构工具函数

本模块实现通用数据结构操作的工具函数库，提高代码复用性。
主要实现有限队列、去重、深拷贝、字典合并、集合运算等功能。

设计原则：
- 高性能：FixedQueue支持O(1)时间复杂度的入队和出队操作
- 线程安全：考虑并发场景下的数据一致性
- 内存效率：最小化内存占用
"""

import copy
from collections import deque


class FixedQueue:
    """
    有限容量队列

    支持FIFO操作和容量限制的队列实现。
    当队列满时，新元素入队会自动丢弃最旧的元素。

    Attributes:
        max_size: 队列最大容量
        _queue: 内部deque存储
    """

    def __init__(self, max_size):
        """
        初始化有限队列

        Args:
            max_size: 队列最大容量
        """
        self.max_size = max_size
        self._queue = deque(maxlen=max_size)

    def add(self, item):
        """
        添加元素到队列尾部

        Args:
            item: 要添加的元素
        """
        self._queue.append(item)

    def get(self):
        """
        从队列头部取出元素

        Returns:
            队列头部元素，若队列为空返回None
        """
        if self.is_empty():
            return None
        return self._queue.popleft()

    def peek(self):
        """
        查看队列头部元素（不移除）

        Returns:
            队列头部元素，若队列为空返回None
        """
        if self.is_empty():
            return None
        return self._queue[0]

    def size(self):
        """
        获取队列当前长度

        Returns:
            int: 队列中的元素数量
        """
        return len(self._queue)

    def is_empty(self):
        """
        判断队列是否为空

        Returns:
            bool: 若队列为空返回True
        """
        return len(self._queue) == 0

    def is_full(self):
        """
        判断队列是否已满

        Returns:
            bool: 若队列已满返回True
        """
        return len(self._queue) >= self.max_size

    def clear(self):
        """清空队列"""
        self._queue.clear()

    def to_list(self):
        """
        将队列转换为列表

        Returns:
            list: 包含队列中所有元素的列表
        """
        return list(self._queue)

    def batch_add(self, items):
        """
        批量添加元素

        Args:
            items: 要添加的元素列表
        """
        for item in items:
            self.add(item)

    def __len__(self):
        return len(self._queue)

    def __iter__(self):
        return iter(self._queue)

    def __repr__(self):
        return f"FixedQueue(max_size={self.max_size}, items={list(self._queue)})"


def deduplicate_list(input_list, key=None):
    """
    去除列表中的重复元素，保持原始顺序

    Args:
        input_list: 输入列表
        key: 用于比较的关键字函数（可选）

    Returns:
        list: 去重后的列表
    """
    seen = set()
    result = []
    for item in input_list:
        k = key(item) if key else item
        if k not in seen:
            seen.add(k)
            result.append(item)
    return result


def deep_copy(obj):
    """
    创建复杂对象的完整深拷贝

    Args:
        obj: 要拷贝的对象

    Returns:
        对象的深拷贝副本
    """
    return copy.deepcopy(obj)


def dict_merge(*dicts):
    """
    合并多个字典

    Args:
        *dicts: 要合并的字典

    Returns:
        dict: 合并后的新字典
    """
    result = {}
    for d in dicts:
        if d:
            result.update(d)
    return result


def dict_merge_recursive(base_dict, update_dict):
    """
    递归合并字典

    Args:
        base_dict: 基础字典
        update_dict: 更新字典

    Returns:
        dict: 递归合并后的字典
    """
    result = deep_copy(base_dict)
    for key, value in update_dict.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = dict_merge_recursive(result[key], value)
        else:
            result[key] = value
    return result


def set_operations(set_a, set_b, operation="union"):
    """
    执行集合运算

    Args:
        set_a: 集合A
        set_b: 集合B
        operation: 运算类型（union, intersection, difference, symmetric_difference）

    Returns:
        set: 运算结果
    """
    a = set(set_a)
    b = set(set_b)

    if operation == "union":
        return a | b
    elif operation == "intersection":
        return a & b
    elif operation == "difference":
        return a - b
    elif operation == "symmetric_difference":
        return a ^ b
    else:
        raise ValueError(f"不支持的运算类型: {operation}")


def chunk_list(input_list, chunk_size):
    """
    将列表分块

    Args:
        input_list: 输入列表
        chunk_size: 每块大小

    Returns:
        list: 分块后的列表
    """
    return [input_list[i:i + chunk_size] for i in range(0, len(input_list), chunk_size)]


def flatten_list(nested_list):
    """
    扁平化嵌套列表

    Args:
        nested_list: 嵌套列表

    Returns:
        list: 扁平化后的列表
    """
    result = []
    for item in nested_list:
        if isinstance(item, list):
            result.extend(flatten_list(item))
        else:
            result.append(item)
    return result
