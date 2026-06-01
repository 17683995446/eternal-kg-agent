# -*- coding: utf-8 -*-
"""
永动知识图谱 Agent - 节点ID生成器
公理溯源: 记忆公理 - 唯一标识是记忆实体可寻址的基础
设计原则: 基于时间戳+随机数生成短ID，确保全局唯一且可读
"""

import os
import time

# 已分配ID集合，用于运行时去重
_allocated_ids = set()


def generate_id() -> str:
    """
    生成全局唯一节点ID。
    公理溯源: 记忆公理 - 唯一ID确保每个记忆实体可被精确引用

    格式: 8位十六进制时间戳 + 4位随机十六进制，共12字符。
    示例: "66a1b2c3d4e5"

    Returns:
        唯一的12字符十六进制ID字符串
    """
    while True:
        ts_hex = format(int(time.time()), "08x")
        rand_hex = os.urandom(2).hex()[:4]
        node_id = ts_hex + rand_hex
        if node_id not in _allocated_ids:
            _allocated_ids.add(node_id)
            return node_id
