"""
节点数据结构

本模块实现知识图谱中的节点数据结构，节点代表系统中的认知实体、任务实例或经验片段。
"""

import uuid
from datetime import datetime, timezone

from config.constants import (
    NODE_STATUS_INITIAL,
    NODE_STATUS_ACTIVE,
    NODE_STATUS_INACTIVE,
    NODE_STATUS_ARCHIVED,
    NODE_STATUS_DELETED,
    NODE_TYPE_TASK,
    NODE_TYPE_COGNITION,
    NODE_TYPE_ENTITY,
)


class Node:
    """
    知识图谱节点

    代表一次任务、一次认知、一个实体经验。

    Attributes:
        node_id: 全局唯一标识符
        node_name: 节点名称字符串
        node_type: 节点类型枚举
        created_at: 创建时间戳
        updated_at: 更新时间戳
        status: 节点状态枚举
        metadata: 元数据字典
    """

    VALID_STATUSES = {
        NODE_STATUS_INITIAL,
        NODE_STATUS_ACTIVE,
        NODE_STATUS_INACTIVE,
        NODE_STATUS_ARCHIVED,
        NODE_STATUS_DELETED,
    }

    VALID_TYPES = {
        NODE_TYPE_TASK,
        NODE_TYPE_COGNITION,
        NODE_TYPE_ENTITY,
    }

    def __init__(self, node_name, node_type=NODE_TYPE_ENTITY, metadata=None, node_id=None):
        """
        初始化节点

        Args:
            node_name: 节点名称
            node_type: 节点类型（默认ENTITY）
            metadata: 元数据字典（可选）
            node_id: 节点ID（可选，默认自动生成）
        """
        self.node_id = node_id or str(uuid.uuid4())
        self.node_name = node_name
        self.node_type = node_type if node_type in self.VALID_TYPES else NODE_TYPE_ENTITY
        self.created_at = datetime.now(timezone.utc).timestamp()
        self.updated_at = self.created_at
        self.status = NODE_STATUS_INITIAL
        self.metadata = metadata or {}

    def activate(self):
        """激活节点"""
        self.status = NODE_STATUS_ACTIVE
        self._update_timestamp()

    def deactivate(self):
        """停用节点"""
        self.status = NODE_STATUS_INACTIVE
        self._update_timestamp()

    def archive(self):
        """归档节点"""
        self.status = NODE_STATUS_ARCHIVED
        self._update_timestamp()

    def delete(self):
        """删除节点"""
        self.status = NODE_STATUS_DELETED
        self._update_timestamp()

    def update_metadata(self, key, value):
        """
        更新元数据

        Args:
            key: 元数据键
            value: 元数据值
        """
        self.metadata[key] = value
        self._update_timestamp()

    def _update_timestamp(self):
        """更新时间戳"""
        self.updated_at = datetime.now(timezone.utc).timestamp()

    def is_active(self):
        """判断节点是否有效"""
        return self.status == NODE_STATUS_ACTIVE

    def to_dict(self):
        """
        将节点序列化为字典

        Returns:
            dict: 节点数据字典
        """
        return {
            "node_id": self.node_id,
            "node_name": self.node_name,
            "node_type": self.node_type,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "status": self.status,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data):
        """
        从字典反序列化节点

        Args:
            data: 节点数据字典

        Returns:
            Node: 节点实例
        """
        node = cls(
            node_name=data["node_name"],
            node_type=data.get("node_type", NODE_TYPE_ENTITY),
            metadata=data.get("metadata", {}),
            node_id=data.get("node_id"),
        )
        node.created_at = data.get("created_at", node.created_at)
        node.updated_at = data.get("updated_at", node.updated_at)
        node.status = data.get("status", NODE_STATUS_INITIAL)
        return node

    def __eq__(self, other):
        if isinstance(other, Node):
            return self.node_id == other.node_id
        return False

    def __hash__(self):
        return hash(self.node_id)

    def __repr__(self):
        return f"Node(id={self.node_id}, name={self.node_name}, type={self.node_type}, status={self.status})"

    def __str__(self):
        return f"{self.node_name}({self.node_type})"
