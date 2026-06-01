"""
边数据结构

本模块实现知识图谱中的边数据结构，边代表节点之间的关联关系和权重信息。
"""

import uuid
from datetime import datetime, timezone

from config.constants import (
    WEIGHT_MAX,
    WEIGHT_MIN,
    WEIGHT_INITIAL,
)


class Edge:
    """
    知识图谱边

    代表实体之间的关联逻辑，附带权重值。
    权重 = 智能经验积累的唯一量化标准。

    Attributes:
        edge_id: 全局唯一标识符
        source: 源节点ID
        target: 目标节点ID
        relation_name: 关系名称字符串
        weight: 权重浮点数（0-1）
        created_at: 创建时间戳
        metadata: 元数据字典
    """

    def __init__(self, source, target, relation_name, weight=None, metadata=None, edge_id=None):
        """
        初始化边

        Args:
            source: 源节点ID
            target: 目标节点ID
            relation_name: 关系名称
            weight: 权重值（可选，默认使用WEIGHT_INITIAL）
            metadata: 元数据字典（可选）
            edge_id: 边ID（可选，默认自动生成）
        """
        self.edge_id = edge_id or str(uuid.uuid4())
        self.source = source
        self.target = target
        self.relation_name = relation_name
        self.weight = self._normalize_weight(weight if weight is not None else WEIGHT_INITIAL)
        self.created_at = datetime.now(timezone.utc).timestamp()
        self.metadata = metadata or {}

    def _normalize_weight(self, weight):
        """
        归一化权重值

        Args:
            weight: 原始权重值

        Returns:
            float: 归一化后的权重值
        """
        return max(WEIGHT_MIN, min(WEIGHT_MAX, float(weight)))

    def update_weight(self, new_weight):
        """
        更新权重

        Args:
            new_weight: 新的权重值
        """
        self.weight = self._normalize_weight(new_weight)

    def increment_weight(self, delta):
        """
        增量更新权重

        Args:
            delta: 权重增量
        """
        self.weight = self._normalize_weight(self.weight + delta)

    def decay_weight(self, decay_rate):
        """
        衰减权重

        Args:
            decay_rate: 衰减率
        """
        self.weight = self._normalize_weight(self.weight * (1 - decay_rate))

    def is_high_value(self, threshold=0.7):
        """
        判断是否高价值关联

        Args:
            threshold: 高价值阈值

        Returns:
            bool: 权重高于阈值返回True
        """
        return self.weight >= threshold

    def is_valid(self, threshold=0.1):
        """
        判断是否有效关联

        Args:
            threshold: 有效阈值

        Returns:
            bool: 权重高于阈值返回True
        """
        return self.weight >= threshold

    def to_dict(self):
        """
        将边序列化为字典

        Returns:
            dict: 边数据字典
        """
        return {
            "edge_id": self.edge_id,
            "source": self.source,
            "target": self.target,
            "relation_name": self.relation_name,
            "weight": self.weight,
            "created_at": self.created_at,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data):
        """
        从字典反序列化边

        Args:
            data: 边数据字典

        Returns:
            Edge: 边实例
        """
        edge = cls(
            source=data["source"],
            target=data["target"],
            relation_name=data["relation_name"],
            weight=data.get("weight"),
            metadata=data.get("metadata", {}),
            edge_id=data.get("edge_id"),
        )
        edge.created_at = data.get("created_at", edge.created_at)
        return edge

    def __eq__(self, other):
        if isinstance(other, Edge):
            return self.edge_id == other.edge_id
        return False

    def __hash__(self):
        return hash(self.edge_id)

    def __repr__(self):
        return f"Edge(id={self.edge_id}, {self.source} -> {self.target}, {self.relation_name}, weight={self.weight:.3f})"

    def __str__(self):
        return f"{self.source} --[{self.relation_name}:{self.weight:.2f}]--> {self.target}"
