# -*- coding: utf-8 -*-
"""
永动知识图谱 Agent - 知识图谱核心类
公理溯源: 记忆公理 - 知识图谱是系统唯一长期记忆载体，
  负责知识的存储、检索、关联与持久化
设计原则: 基于Node/Edge数据结构，支持CRUD操作与JSON持久化
"""

import json
import os
import time

from src.config import KG_SAVE_PATH
from src.kg.edge import Edge
from src.kg.id_generator import generate_id
from src.kg.node import Node
from src.logger import get_logger

logger = get_logger("kg")


class KnowledgeGraph:
    """
    知识图谱核心类。
    公理溯源: 记忆公理 - 知识图谱封装所有记忆实体与关系，
    提供统一的增删改查接口，是系统记忆的完整抽象。
    """

    def __init__(self, save_path: str = None):
        """
        初始化知识图谱。
        公理溯源: 记忆公理 - 初始化时从持久化存储恢复记忆

        Args:
            save_path: 持久化文件路径，默认使用config中的配置
        """
        self.nodes: dict[str, Node] = {}
        self.edges: list[Edge] = []
        self._name_index: dict[str, str] = {}  # name -> node_id 映射
        self.save_path = save_path or KG_SAVE_PATH
        self.load()

    # ================================================================
    # 节点操作
    # 公理溯源: 记忆公理 - 节点是记忆的基本单元
    # ================================================================

    def add_node(self, name: str, attr: dict = None) -> Node:
        """
        添加节点（按名称去重）。
        公理溯源: 记忆公理 - 去重确保记忆中同一实体不会重复存在

        Args:
            name: 节点名称
            attr: 自定义属性

        Returns:
            新创建或已存在的Node实例
        """
        if name in self._name_index:
            return self.nodes[self._name_index[name]]

        node = Node(node_id=generate_id(), name=name, attributes=attr)
        self.nodes[node.id] = node
        self._name_index[name] = node.id
        logger.debug(f"添加节点: {name} ({node.id})")
        return node

    def get_node(self, node_id: str) -> Node | None:
        """
        根据ID获取节点。
        公理溯源: 记忆公理 - 精确检索是记忆利用的基础

        Args:
            node_id: 节点ID

        Returns:
            Node实例或None
        """
        return self.nodes.get(node_id)

    def get_node_by_name(self, name: str) -> Node | None:
        """
        根据名称获取节点。
        公理溯源: 记忆公理 - 名称检索提供记忆的语义访问方式

        Args:
            name: 节点名称

        Returns:
            Node实例或None
        """
        node_id = self._name_index.get(name)
        if node_id is None:
            return None
        return self.nodes.get(node_id)

    def node_exists(self, node_id: str) -> bool:
        """
        检查节点是否存在。
        公理溯源: 记忆公理 - 存在性检查是记忆操作的前提条件

        Args:
            node_id: 节点ID

        Returns:
            是否存在
        """
        return node_id in self.nodes

    def remove_node(self, node_id: str) -> bool:
        """
        删除节点及其关联的所有边。
        公理溯源: 记忆公理 - 删除操作是记忆修正的一部分

        Args:
            node_id: 节点ID

        Returns:
            是否成功删除
        """
        node = self.nodes.get(node_id)
        if node is None:
            return False

        # 从名称索引中移除
        self._name_index.pop(node.name, None)

        # 删除关联的所有边
        self.edges = [
            e for e in self.edges
            if e.source_id != node_id and e.target_id != node_id
        ]

        del self.nodes[node_id]
        logger.debug(f"删除节点: {node.name} ({node_id})")
        return True

    def invalidate_node(self, node_id: str) -> bool:
        """
        标记节点为无效（软删除）。
        公理溯源: 记忆公理 - 软删除保留记忆痕迹，支持未来恢复

        Args:
            node_id: 节点ID

        Returns:
            是否成功标记
        """
        node = self.nodes.get(node_id)
        if node is None:
            return False
        node.is_valid = False
        node.updated_at = time.time()
        logger.debug(f"标记节点无效: {node.name} ({node_id})")
        return True

    # ================================================================
    # 边操作
    # 公理溯源: 记忆公理 - 边是记忆中实体间关系的载体
    # ================================================================

    def add_edge(self, source: str, target: str, relation_name: str,
                 weight: float = 0.5) -> Edge:
        """
        添加边（自动创建头尾节点，按三元组去重）。
        公理溯源: 记忆公理 - 边的自动创建确保关系表达不会因节点缺失而失败

        Args:
            source: 源节点名称
            target: 目标节点名称
            relation_name: 关系名称
            weight: 关系权重

        Returns:
            新创建或已存在的Edge实例
        """
        source_node = self.add_node(source)
        target_node = self.add_node(target)

        # 按三元组去重
        for edge in self.edges:
            if (edge.source_id == source_node.id
                    and edge.target_id == target_node.id
                    and edge.relation_name == relation_name):
                return edge

        edge = Edge(
            source_id=source_node.id,
            target_id=target_node.id,
            relation_name=relation_name,
            weight=weight,
        )
        self.edges.append(edge)
        logger.debug(f"添加边: {source} --[{relation_name}]--> {target}")
        return edge

    def get_edges_by_source(self, source_id: str) -> list[Edge]:
        """
        获取以指定节点为源的所有边。
        公理溯源: 记忆公理 - 关系检索支持记忆的关联遍历

        Args:
            source_id: 源节点ID

        Returns:
            Edge列表
        """
        return [e for e in self.edges if e.source_id == source_id]

    def get_edges_by_target(self, target_id: str) -> list[Edge]:
        """
        获取以指定节点为目标的所有边。
        公理溯源: 记忆公理 - 反向检索支持记忆的逆向关联遍历

        Args:
            target_id: 目标节点ID

        Returns:
            Edge列表
        """
        return [e for e in self.edges if e.target_id == target_id]

    def get_edges_by_relation(self, relation: str) -> list[Edge]:
        """
        获取指定关系名称的所有边。
        公理溯源: 记忆公理 - 按关系类型检索支持知识的分类查询

        Args:
            relation: 关系名称

        Returns:
            Edge列表
        """
        return [e for e in self.edges if e.relation_name == relation]

    def remove_edge(self, source_id: str, target_id: str,
                    relation_name: str) -> bool:
        """
        删除指定的边。
        公理溯源: 记忆公理 - 关系删除是记忆修正的一部分

        Args:
            source_id: 源节点ID
            target_id: 目标节点ID
            relation_name: 关系名称

        Returns:
            是否成功删除
        """
        original_len = len(self.edges)
        self.edges = [
            e for e in self.edges
            if not (e.source_id == source_id
                    and e.target_id == target_id
                    and e.relation_name == relation_name)
        ]
        removed = len(self.edges) < original_len
        if removed:
            logger.debug(f"删除边: {source_id} --[{relation_name}]--> {target_id}")
        return removed

    # ================================================================
    # 持久化
    # 公理溯源: 记忆公理 - 持久化确保记忆在系统重启后可恢复
    # ================================================================

    def save(self) -> None:
        """
        序列化知识图谱到JSON文件。
        公理溯源: 记忆公理 - 持久化是记忆跨越时间存续的唯一手段
        """
        data = {
            "nodes": [node.to_dict() for node in self.nodes.values()],
            "edges": [edge.to_dict() for edge in self.edges],
        }
        save_dir = os.path.dirname(self.save_path)
        if save_dir:
            os.makedirs(save_dir, exist_ok=True)
        with open(self.save_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.debug(f"知识图谱已保存: {self.save_path}")

    def load(self) -> None:
        """
        从JSON文件反序列化知识图谱。
        公理溯源: 记忆公理 - 加载是系统启动时记忆恢复的必要步骤
        """
        if not os.path.exists(self.save_path):
            logger.debug("知识图谱文件不存在，使用空图谱初始化")
            return

        try:
            with open(self.save_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.nodes.clear()
            self._name_index.clear()
            self.edges.clear()

            for node_data in data.get("nodes", []):
                node = Node.from_dict(node_data)
                self.nodes[node.id] = node
                self._name_index[node.name] = node.id

            for edge_data in data.get("edges", []):
                edge = Edge.from_dict(edge_data)
                self.edges.append(edge)

            logger.info(f"知识图谱已加载: {len(self.nodes)}个节点, {len(self.edges)}条边")
        except (json.JSONDecodeError, KeyError, UnicodeDecodeError, TypeError) as e:
            logger.warning(f"知识图谱加载失败，使用空图谱初始化: {e}")

    # ================================================================
    # 统计
    # 公理溯源: 存续公理 - 统计信息是系统感知自身状态的基础
    # ================================================================

    def get_stats(self) -> dict:
        """
        获取知识图谱统计信息。
        公理溯源: 存续公理 - 统计数据反映系统的记忆规模与健康状态

        Returns:
            包含节点总数、边总数、有效节点数、平均权重的字典
        """
        total_nodes = len(self.nodes)
        total_edges = len(self.edges)
        valid_nodes = sum(1 for n in self.nodes.values() if n.is_valid)
        avg_weight = (
            sum(e.weight for e in self.edges) / total_edges
            if total_edges > 0
            else 0.0
        )
        return {
            "total_nodes": total_nodes,
            "total_edges": total_edges,
            "valid_nodes": valid_nodes,
            "avg_weight": round(avg_weight, 4),
        }

    # ================================================================
    # 知识推演与自驱
    # 公理溯源: 自驱公理 - 推演是系统从已有知识中主动发现新任务的机制
    # ================================================================

    def derive_new_tasks(self, node_name: str,
                         weight_threshold: float = 0.2) -> list[str]:
        """
        从指定节点推演新任务。
        公理溯源: 自驱公理 - 基于关联权重推演任务，实现知识的主动扩展

        Args:
            node_name: 源节点名称
            weight_threshold: 权重阈值，仅推演超过该阈值的关联

        Returns:
            去重后的推演任务名列表
        """
        node = self.get_node_by_name(node_name)
        if node is None:
            return []
        tasks = []
        seen = set()
        for edge in self.edges:
            if edge.source_id == node.id and edge.weight > weight_threshold:
                target = self.nodes.get(edge.target_id)
                if target and target.name not in seen:
                    seen.add(target.name)
                    tasks.append(f"知识推演任务:{target.name}")
        return tasks

    def derive_multi_hop_tasks(self, node_name: str, max_hops: int = 2,
                               weight_threshold: float = 0.2) -> list[str]:
        """
        多跳关联推演任务。
        公理溯源: 自驱公理 - 多跳推演扩展系统的知识发现半径

        Args:
            node_name: 起始节点名称
            max_hops: 最大跳数
            weight_threshold: 权重阈值

        Returns:
            去重后的推演任务名列表
        """
        node = self.get_node_by_name(node_name)
        if node is None:
            return []
        tasks = []
        seen = set()
        # 第一跳
        hop1_edges = [e for e in self.edges
                      if e.source_id == node.id and e.weight > weight_threshold]
        for edge in hop1_edges:
            target = self.nodes.get(edge.target_id)
            if target and target.name not in seen:
                seen.add(target.name)
                tasks.append(f"知识推演任务:{target.name}")
            # 第二跳
            if max_hops >= 2 and target:
                for e2 in self.edges:
                    if (e2.source_id == target.id
                            and e2.weight > weight_threshold):
                        t2 = self.nodes.get(e2.target_id)
                        if t2 and t2.name not in seen:
                            seen.add(t2.name)
                            tasks.append(f"知识推演任务:{t2.name}")
        return tasks

    def get_derive_frequency_control(self) -> set:
        """
        获取推演频率控制集合。
        公理溯源: 自驱公理 - 频率控制防止同一节点被重复推演，保障资源效率

        Returns:
            已推演节点名的集合
        """
        if not hasattr(self, "_derived_nodes"):
            self._derived_nodes = set()
        return self._derived_nodes

    # ================================================================
    # 知识进化与精简
    # 公理溯源: 自驱公理 - 进化是系统自我优化的核心机制
    # ================================================================

    def trim_invalid_knowledge(self, weight_threshold: float = 0.1) -> dict:
        """
        修剪无效知识：删除低权重边和孤立节点。
        公理溯源: 自驱公理 - 修剪移除冗余记忆，提升知识图谱的信噪比

        Args:
            weight_threshold: 权重阈值，删除权重<=该值的边

        Returns:
            修剪统计：删除的边数和节点数
        """
        before = self.get_stats()
        # 删除低权重边
        self.edges = [e for e in self.edges if e.weight > weight_threshold]
        # 清理孤立节点
        connected_ids = set()
        for e in self.edges:
            connected_ids.add(e.source_id)
            connected_ids.add(e.target_id)
        orphan_ids = [nid for nid in self.nodes if nid not in connected_ids]
        for nid in orphan_ids:
            self.remove_node(nid)
        after = self.get_stats()
        self.save()
        return {
            "edges_removed": before["total_edges"] - after["total_edges"],
            "nodes_removed": before["total_nodes"] - after["total_nodes"],
        }

    def decay_edges(self, decay_factor: float = 0.95) -> None:
        """
        衰减所有边的权重。
        公理溯源: 自驱公理 - 衰减使不活跃的知识逐渐退化，确保记忆的新鲜度

        Args:
            decay_factor: 衰减系数，每条边权重乘以该值
        """
        for edge in self.edges:
            edge.weight *= decay_factor
        self.save()

    def strengthen_edge(self, source_name: str, target_name: str,
                         relation_name: str, boost: float = 0.1) -> bool:
        """
        增强指定边的权重。
        公理溯源: 自驱公理 - 强化使活跃知识保持高权重，形成正反馈

        Args:
            source_name: 源节点名称
            target_name: 目标节点名称
            relation_name: 关系名称
            boost: 增强幅度

        Returns:
            是否成功增强
        """
        src = self.get_node_by_name(source_name)
        tgt = self.get_node_by_name(target_name)
        if src is None or tgt is None:
            return False
        for edge in self.edges:
            if (edge.source_id == src.id
                    and edge.target_id == tgt.id
                    and edge.relation_name == relation_name):
                edge.weight = min(1.0, edge.weight + boost)
                self.save()
                return True
        return False

    def normalize_weights(self) -> None:
        """
        归一化所有边权重到[0,1]区间。
        公理溯源: 自驱公理 - 归一化统一权重尺度，使进化过程可度量

        如果最大权重为0（所有边权重为0），则不做任何操作。
        """
        if not self.edges:
            return
        max_w = max(e.weight for e in self.edges)
        if max_w <= 0:
            return
        for edge in self.edges:
            edge.weight = edge.weight / max_w
        self.save()

    def backup_graph(self, backup_dir: str = "data/backups",
                     max_backups: int = 5) -> str | None:
        """
        备份当前图谱文件。
        公理溯源: 自驱公理 - 备份是系统自我保护的机制，防止进化失误导致记忆丢失

        Args:
            backup_dir: 备份目录
            max_backups: 最大备份数量

        Returns:
            备份文件路径，失败返回None
        """
        import shutil
        import time as _time
        if not os.path.exists(self.save_path):
            return None
        os.makedirs(backup_dir, exist_ok=True)
        ts = _time.strftime("%Y%m%d_%H%M%S") + f"_{_time.time_ns() % 1000000:06d}"
        filename = f"kg_backup_{ts}.json"
        dest = os.path.join(backup_dir, filename)
        shutil.copy2(self.save_path, dest)
        # 只保留最近N份备份
        backups = sorted(
            [f for f in os.listdir(backup_dir) if f.startswith("kg_backup_")],
            reverse=True,
        )
        for old in backups[max_backups:]:
            os.remove(os.path.join(backup_dir, old))
        logger.info(f"知识图谱已备份: {dest}")
        return dest

    def get_evolution_report(self) -> dict:
        """
        获取进化报告。
        公理溯源: 自驱公理 - 进化报告使系统的自我优化过程可追溯

        Returns:
            包含节点数/边数变化的报告字典
        """
        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "valid_nodes": sum(1 for n in self.nodes.values() if n.is_valid),
            "avg_weight": round(
                sum(e.weight for e in self.edges) / len(self.edges), 4
            ) if self.edges else 0.0,
        }
