# -*- coding: utf-8 -*-
"""
永动知识图谱 Agent - 边数据结构
公理溯源: 记忆公理 - 边是知识图谱中实体间关系的载体，构成记忆网络的连接
设计原则: 轻量级数据结构，支持序列化与反序列化，便于持久化存储
"""

import time


class Edge:
    """
    知识图谱边。
    公理溯源: 记忆公理 - 边连接两个节点，表达实体间的关系，
    是记忆网络中知识关联的基本表达形式。
    """

    def __init__(self, source_id: str, target_id: str, relation_name: str,
                 weight: float = 0.5):
        """
        初始化边。
        公理溯源: 记忆公理 - 边的三元组(源,目标,关系)定义了知识的关联结构

        Args:
            source_id: 源节点ID
            target_id: 目标节点ID
            relation_name: 关系名称
            weight: 关系权重，默认0.5，范围[0.0, 1.0]
        """
        self.source_id = source_id
        self.target_id = target_id
        self.relation_name = relation_name
        self.weight = weight
        self.created_at = time.time()

    def to_dict(self) -> dict:
        """
        序列化为字典。
        公理溯源: 记忆公理 - 序列化是记忆持久化的必要步骤

        Returns:
            包含边所有属性的字典
        """
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relation_name": self.relation_name,
            "weight": self.weight,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Edge":
        """
        从字典反序列化为边。
        公理溯源: 记忆公理 - 反序列化是记忆恢复的必要步骤

        Args:
            data: 包含边属性的字典

        Returns:
            Edge实例
        """
        edge = cls(
            source_id=data["source_id"],
            target_id=data["target_id"],
            relation_name=data["relation_name"],
            weight=data.get("weight", 0.5),
        )
        edge.created_at = data.get("created_at", time.time())
        return edge
