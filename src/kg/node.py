# -*- coding: utf-8 -*-
"""
永动知识图谱 Agent - 节点数据结构
公理溯源: 记忆公理 - 节点是知识图谱记忆的基本单元，承载实体信息
设计原则: 轻量级数据结构，支持序列化与反序列化，便于持久化存储
"""

import time


class Node:
    """
    知识图谱节点。
    公理溯源: 记忆公理 - 每个节点代表一个知识实体，
    是记忆网络中不可再分的基本单元。
    """

    def __init__(self, node_id: str, name: str, attributes: dict = None):
        """
        初始化节点。
        公理溯源: 记忆公理 - 节点的唯一标识确保记忆实体可精确定位

        Args:
            node_id: 唯一标识符
            name: 节点名称
            attributes: 自定义属性字典，默认为空
        """
        self.id = node_id
        self.name = name
        self.attributes = attributes if attributes is not None else {}
        self.created_at = time.time()
        self.is_valid = True
        self.updated_at = self.created_at

    def to_dict(self) -> dict:
        """
        序列化为字典。
        公理溯源: 记忆公理 - 序列化是记忆持久化的必要步骤

        Returns:
            包含节点所有属性的字典
        """
        return {
            "id": self.id,
            "name": self.name,
            "attributes": self.attributes,
            "created_at": self.created_at,
            "is_valid": self.is_valid,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Node":
        """
        从字典反序列化为节点。
        公理溯源: 记忆公理 - 反序列化是记忆恢复的必要步骤

        Args:
            data: 包含节点属性的字典

        Returns:
            Node实例
        """
        node = cls(
            node_id=data["id"],
            name=data["name"],
            attributes=data.get("attributes", {}),
        )
        node.created_at = data.get("created_at", time.time())
        node.is_valid = data.get("is_valid", True)
        node.updated_at = data.get("updated_at", node.created_at)
        return node
