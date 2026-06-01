"""
知识图谱核心引擎

本模块实现知识图谱的主类，整合节点和边的管理，构建完整的知识存储和管理系统。
"""

import json
from pathlib import Path

from config.constants import (
    KG_SAVE_PATH,
    KG_VERSION,
    KG_AUTOSAVE_THRESHOLD,
    KG_BACKUP_ENABLED,
    WEIGHT_THRESHOLD_INVALID,
    WEIGHT_THRESHOLD_HIGH,
    NODE_STATUS_ACTIVE,
    NODE_STATUS_DELETED,
    RELATION_DERIVED,
)
from models.node import Node
from models.edge import Edge
from utils.file_utils import safe_read_json, safe_write_json, file_exists
from utils.time_utils import get_timestamp


class KnowledgeGraph:
    """
    知识图谱主类

    管理节点和边的生命周期，提供统一的图谱操作接口。

    Attributes:
        nodes: 节点字典 {node_id: Node}
        edges: 边列表 [Edge]
        _change_count: 变更计数器
        _version: 图谱版本号
    """

    def __init__(self, save_path=None):
        """
        初始化知识图谱

        Args:
            save_path: 持久化文件路径（可选）
        """
        self.save_path = save_path or KG_SAVE_PATH
        self.nodes = {}
        self.edges = []
        self._change_count = 0
        self._version = KG_VERSION
        self._node_name_index = {}
        self._edge_source_index = {}
        self._edge_target_index = {}

        self.load()

    def add_node(self, name, node_type=None, metadata=None):
        """
        添加节点

        Args:
            name: 节点名称
            node_type: 节点类型（可选）
            metadata: 元数据（可选）

        Returns:
            Node: 新创建的节点
        """
        existing = self.find_node_by_name(name)
        if existing:
            return existing

        node = Node(name, node_type, metadata)
        self.nodes[node.node_id] = node
        self._node_name_index[name] = node.node_id
        self._on_change()
        return node

    def get_node(self, node_id):
        """
        获取节点

        Args:
            node_id: 节点ID

        Returns:
            Node: 节点实例，不存在返回None
        """
        return self.nodes.get(node_id)

    def find_node_by_name(self, name):
        """
        根据名称查找节点

        Args:
            name: 节点名称

        Returns:
            Node: 节点实例，不存在返回None
        """
        node_id = self._node_name_index.get(name)
        if node_id:
            return self.nodes.get(node_id)
        return None

    def update_node(self, node_id, **kwargs):
        """
        更新节点

        Args:
            node_id: 节点ID
            **kwargs: 要更新的属性

        Returns:
            bool: 更新成功返回True
        """
        node = self.nodes.get(node_id)
        if not node:
            return False

        if "metadata" in kwargs:
            node.metadata.update(kwargs["metadata"])
        if "status" in kwargs:
            node.status = kwargs["status"]

        node._update_timestamp()
        self._on_change()
        return True

    def delete_node(self, node_id):
        """
        删除节点

        Args:
            node_id: 节点ID

        Returns:
            bool: 删除成功返回True
        """
        node = self.nodes.get(node_id)
        if not node:
            return False

        node.delete()
        self.edges = [e for e in self.edges if e.source != node_id and e.target != node_id]
        self._rebuild_indexes()
        self._on_change()
        return True

    def add_edge(self, source, target, relation_name, weight=None, metadata=None):
        """
        添加边

        Args:
            source: 源节点ID或名称
            target: 目标节点ID或名称
            relation_name: 关系名称
            weight: 权重（可选）
            metadata: 元数据（可选）

        Returns:
            Edge: 新创建的边
        """
        source_node = self._resolve_node(source)
        target_node = self._resolve_node(target)

        if not source_node or not target_node:
            return None

        edge = Edge(source_node.node_id, target_node.node_id, relation_name, weight, metadata)
        self.edges.append(edge)
        self._update_edge_indexes(edge)
        self._on_change()
        return edge

    def get_edges_by_source(self, node_id):
        """
        获取指定源节点的所有出边

        Args:
            node_id: 节点ID

        Returns:
            list: 边列表
        """
        return [self.edges[i] for i in self._edge_source_index.get(node_id, [])]

    def get_edges_by_target(self, node_id):
        """
        获取指定目标节点的所有入边

        Args:
            node_id: 节点ID

        Returns:
            list: 边列表
        """
        return [self.edges[i] for i in self._edge_target_index.get(node_id, [])]

    def derive_new_tasks(self, node_name, weight_threshold=0.2):
        """
        基于已有知识推演新生任务

        Args:
            node_name: 起始节点名称
            weight_threshold: 权重阈值

        Returns:
            list: 推演出的新任务列表
        """
        node = self.find_node_by_name(node_name)
        if not node:
            return []

        new_tasks = []
        edges = self.get_edges_by_source(node.node_id)

        for edge in edges:
            if edge.weight > weight_threshold:
                target_node = self.get_node(edge.target)
                if target_node:
                    new_tasks.append(f"知识推演任务:{target_node.node_name}")

        return list(set(new_tasks))

    def trim_invalid_knowledge(self):
        """
        自动淘汰低价值知识

        Returns:
            tuple: (被移除的边数量, 被移除的节点数量)
        """
        original_edge_count = len(self.edges)
        self.edges = [e for e in self.edges if e.is_valid(WEIGHT_THRESHOLD_INVALID)]
        removed_edges = original_edge_count - len(self.edges)

        active_node_ids = set()
        for edge in self.edges:
            active_node_ids.add(edge.source)
            active_node_ids.add(edge.target)

        original_node_count = len(self.nodes)
        self.nodes = {k: v for k, v in self.nodes.items() if k in active_node_ids}
        removed_nodes = original_node_count - len(self.nodes)

        self._rebuild_indexes()
        self._on_change()
        return removed_edges, removed_nodes

    def get_stats(self):
        """
        获取图谱统计信息

        Returns:
            dict: 统计信息字典
        """
        return {
            "node_count": len(self.nodes),
            "edge_count": len(self.edges),
            "version": self._version,
            "avg_weight": sum(e.weight for e in self.edges) / len(self.edges) if self.edges else 0,
        }

    def save(self):
        """
        保存图谱到文件

        Returns:
            bool: 保存成功返回True
        """
        data = {
            "version": self._version,
            "nodes": [node.to_dict() for node in self.nodes.values()],
            "edges": [edge.to_dict() for edge in self.edges],
            "metadata": {
                "saved_at": get_timestamp(),
                "node_count": len(self.nodes),
                "edge_count": len(self.edges),
            },
        }
        return safe_write_json(self.save_path, data)

    def load(self):
        """
        从文件加载图谱

        Returns:
            bool: 加载成功返回True
        """
        if not file_exists(self.save_path):
            return False

        data = safe_read_json(self.save_path)
        if not data:
            return False

        self._version = data.get("version", KG_VERSION)

        for node_data in data.get("nodes", []):
            node = Node.from_dict(node_data)
            self.nodes[node.node_id] = node

        for edge_data in data.get("edges", []):
            edge = Edge.from_dict(edge_data)
            self.edges.append(edge)

        self._rebuild_indexes()
        return True

    def _resolve_node(self, node_ref):
        """
        解析节点引用（ID或名称）

        Args:
            node_ref: 节点ID或名称

        Returns:
            Node: 节点实例
        """
        if isinstance(node_ref, Node):
            return node_ref

        node = self.nodes.get(node_ref)
        if node:
            return node

        return self.find_node_by_name(node_ref)

    def _on_change(self):
        """变更回调"""
        self._change_count += 1
        if self._change_count >= KG_AUTOSAVE_THRESHOLD:
            self.save()
            self._change_count = 0

    def _rebuild_indexes(self):
        """重建索引"""
        self._node_name_index = {}
        self._edge_source_index = {}
        self._edge_target_index = {}

        for node_id, node in self.nodes.items():
            self._node_name_index[node.node_name] = node_id

        for i, edge in enumerate(self.edges):
            self._edge_source_index.setdefault(edge.source, []).append(i)
            self._edge_target_index.setdefault(edge.target, []).append(i)

    def _update_edge_indexes(self, edge):
        """更新边索引"""
        index = len(self.edges) - 1
        self._edge_source_index.setdefault(edge.source, []).append(index)
        self._edge_target_index.setdefault(edge.target, []).append(index)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.save()
        return False

    def __repr__(self):
        return f"KnowledgeGraph(nodes={len(self.nodes)}, edges={len(self.edges)}, version={self._version})"
