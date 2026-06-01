# -*- coding: utf-8 -*-
"""
永动知识图谱 Agent - 知识图谱模块集成测试（阶段11-25）
公理溯源: 存续公理 - 集成测试验证知识图谱核心模块的完整功能
设计原则: 覆盖CRUD全流程：创建->查询->修改->删除->持久化->重启恢复
"""

import os
import sys
import tempfile
import time
import unittest

# 确保项目根目录在搜索路径中
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.kg.edge import Edge
from src.kg.id_generator import generate_id
from src.kg.knowledge_graph import KnowledgeGraph
from src.kg.node import Node


# ================================================================
# 阶段11: Node 数据结构测试
# ================================================================

class TestNode(unittest.TestCase):
    """验证Node数据结构的创建与序列化"""

    def test_node_creation(self):
        """Node应正确初始化所有属性"""
        node = Node(node_id="abc123", name="测试节点")
        self.assertEqual(node.id, "abc123")
        self.assertEqual(node.name, "测试节点")
        self.assertEqual(node.attributes, {})
        self.assertTrue(node.is_valid)
        self.assertIsInstance(node.created_at, float)
        self.assertEqual(node.created_at, node.updated_at)

    def test_node_with_attributes(self):
        """Node应支持自定义属性"""
        node = Node(node_id="abc123", name="测试", attributes={"key": "value"})
        self.assertEqual(node.attributes["key"], "value")

    def test_node_to_dict(self):
        """Node.to_dict()应返回包含所有属性的字典"""
        node = Node(node_id="abc123", name="测试节点")
        d = node.to_dict()
        self.assertEqual(d["id"], "abc123")
        self.assertEqual(d["name"], "测试节点")
        self.assertIn("attributes", d)
        self.assertIn("created_at", d)
        self.assertIn("is_valid", d)
        self.assertIn("updated_at", d)

    def test_node_from_dict(self):
        """Node.from_dict()应正确还原Node实例"""
        data = {
            "id": "xyz789",
            "name": "还原节点",
            "attributes": {"a": 1},
            "created_at": 1000.0,
            "is_valid": True,
            "updated_at": 1001.0,
        }
        node = Node.from_dict(data)
        self.assertEqual(node.id, "xyz789")
        self.assertEqual(node.name, "还原节点")
        self.assertEqual(node.attributes, {"a": 1})
        self.assertEqual(node.created_at, 1000.0)
        self.assertTrue(node.is_valid)
        self.assertEqual(node.updated_at, 1001.0)

    def test_node_roundtrip(self):
        """Node序列化->反序列化应保持数据一致"""
        original = Node(node_id="rt001", name="往返测试", attributes={"x": 42})
        restored = Node.from_dict(original.to_dict())
        self.assertEqual(original.id, restored.id)
        self.assertEqual(original.name, restored.name)
        self.assertEqual(original.attributes, restored.attributes)
        self.assertEqual(original.created_at, restored.created_at)
        self.assertEqual(original.is_valid, restored.is_valid)


# ================================================================
# 阶段12: Edge 数据结构测试
# ================================================================

class TestEdge(unittest.TestCase):
    """验证Edge数据结构的创建与序列化"""

    def test_edge_creation(self):
        """Edge应正确初始化所有属性"""
        edge = Edge(source_id="s1", target_id="t1", relation_name="关联")
        self.assertEqual(edge.source_id, "s1")
        self.assertEqual(edge.target_id, "t1")
        self.assertEqual(edge.relation_name, "关联")
        self.assertEqual(edge.weight, 0.5)
        self.assertIsInstance(edge.created_at, float)

    def test_edge_custom_weight(self):
        """Edge应支持自定义权重"""
        edge = Edge(source_id="s1", target_id="t1", relation_name="关联", weight=0.9)
        self.assertEqual(edge.weight, 0.9)

    def test_edge_to_dict(self):
        """Edge.to_dict()应返回包含所有属性的字典"""
        edge = Edge(source_id="s1", target_id="t1", relation_name="关联")
        d = edge.to_dict()
        self.assertEqual(d["source_id"], "s1")
        self.assertEqual(d["target_id"], "t1")
        self.assertEqual(d["relation_name"], "关联")
        self.assertEqual(d["weight"], 0.5)
        self.assertIn("created_at", d)

    def test_edge_from_dict(self):
        """Edge.from_dict()应正确还原Edge实例"""
        data = {
            "source_id": "s2",
            "target_id": "t2",
            "relation_name": "依赖",
            "weight": 0.8,
            "created_at": 2000.0,
        }
        edge = Edge.from_dict(data)
        self.assertEqual(edge.source_id, "s2")
        self.assertEqual(edge.target_id, "t2")
        self.assertEqual(edge.relation_name, "依赖")
        self.assertEqual(edge.weight, 0.8)
        self.assertEqual(edge.created_at, 2000.0)

    def test_edge_roundtrip(self):
        """Edge序列化->反序列化应保持数据一致"""
        original = Edge(source_id="s1", target_id="t1", relation_name="测试", weight=0.3)
        restored = Edge.from_dict(original.to_dict())
        self.assertEqual(original.source_id, restored.source_id)
        self.assertEqual(original.target_id, restored.target_id)
        self.assertEqual(original.relation_name, restored.relation_name)
        self.assertEqual(original.weight, restored.weight)


# ================================================================
# 阶段13: ID生成器测试
# ================================================================

class TestIdGenerator(unittest.TestCase):
    """验证节点ID生成器的唯一性与格式"""

    def test_id_format(self):
        """生成的ID应为12字符十六进制字符串"""
        id1 = generate_id()
        self.assertEqual(len(id1), 12)
        self.assertTrue(all(c in "0123456789abcdef" for c in id1))

    def test_id_uniqueness(self):
        """连续生成的100个ID应全部唯一"""
        ids = {generate_id() for _ in range(100)}
        self.assertEqual(len(ids), 100)

    def test_id_global_dedup(self):
        """同一ID不应被重复分配"""
        # generate_id内部维护去重集合，此处验证其机制
        ids = [generate_id() for _ in range(50)]
        self.assertEqual(len(ids), len(set(ids)))


# ================================================================
# 阶段14-24: KnowledgeGraph 核心类测试
# ================================================================

class TestKnowledgeGraphCRUD(unittest.TestCase):
    """验证知识图谱的完整CRUD操作"""

    def setUp(self):
        """每个测试用例使用独立的临时目录"""
        self.tmp_dir = tempfile.mkdtemp()
        self.save_path = os.path.join(self.tmp_dir, "test_kg.json")
        self.kg = KnowledgeGraph(save_path=self.save_path)

    # ---- 创建操作 ----

    def test_add_node(self):
        """add_node应创建节点并返回Node实例"""
        node = self.kg.add_node("Python")
        self.assertIsInstance(node, Node)
        self.assertEqual(node.name, "Python")
        self.assertTrue(self.kg.node_exists(node.id))

    def test_add_node_dedup(self):
        """add_node按名称去重，同名返回已有节点"""
        node1 = self.kg.add_node("Python")
        node2 = self.kg.add_node("Python")
        self.assertEqual(node1.id, node2.id)

    def test_add_node_with_attr(self):
        """add_node应支持自定义属性"""
        node = self.kg.add_node("AI", attr={"type": "概念"})
        self.assertEqual(node.attributes["type"], "概念")

    def test_add_edge(self):
        """add_edge应创建边并自动创建头尾节点"""
        edge = self.kg.add_edge("Python", "编程语言", "is_a")
        self.assertIsInstance(edge, Edge)
        self.assertEqual(edge.relation_name, "is_a")
        self.assertTrue(self.kg.node_exists(edge.source_id))
        self.assertTrue(self.kg.node_exists(edge.target_id))

    def test_add_edge_dedup(self):
        """add_edge按三元组去重"""
        edge1 = self.kg.add_edge("A", "B", "关联")
        edge2 = self.kg.add_edge("A", "B", "关联")
        self.assertEqual(edge1.source_id, edge2.source_id)
        self.assertEqual(edge1.target_id, edge2.target_id)

    def test_add_edge_custom_weight(self):
        """add_edge应支持自定义权重"""
        edge = self.kg.add_edge("A", "B", "关联", weight=0.9)
        self.assertEqual(edge.weight, 0.9)

    # ---- 查询操作 ----

    def test_get_node(self):
        """get_node应通过ID获取节点"""
        node = self.kg.add_node("Python")
        found = self.kg.get_node(node.id)
        self.assertIsNotNone(found)
        self.assertEqual(found.name, "Python")

    def test_get_node_not_found(self):
        """get_node对不存在的ID返回None"""
        self.assertIsNone(self.kg.get_node("nonexistent"))

    def test_get_node_by_name(self):
        """get_node_by_name应通过名称获取节点"""
        self.kg.add_node("Python")
        found = self.kg.get_node_by_name("Python")
        self.assertIsNotNone(found)
        self.assertEqual(found.name, "Python")

    def test_get_node_by_name_not_found(self):
        """get_node_by_name对不存在的名称返回None"""
        self.assertIsNone(self.kg.get_node_by_name("不存在"))

    def test_node_exists(self):
        """node_exists应正确判断节点是否存在"""
        node = self.kg.add_node("Python")
        self.assertTrue(self.kg.node_exists(node.id))
        self.assertFalse(self.kg.node_exists("nonexistent"))

    def test_get_edges_by_source(self):
        """get_edges_by_source应返回指定源节点的所有出边"""
        self.kg.add_edge("A", "B", "r1")
        self.kg.add_edge("A", "C", "r2")
        node_a = self.kg.get_node_by_name("A")
        edges = self.kg.get_edges_by_source(node_a.id)
        self.assertEqual(len(edges), 2)

    def test_get_edges_by_target(self):
        """get_edges_by_target应返回指定目标节点的所有入边"""
        self.kg.add_edge("A", "C", "r1")
        self.kg.add_edge("B", "C", "r2")
        node_c = self.kg.get_node_by_name("C")
        edges = self.kg.get_edges_by_target(node_c.id)
        self.assertEqual(len(edges), 2)

    def test_get_edges_by_relation(self):
        """get_edges_by_relation应返回指定关系的所有边"""
        self.kg.add_edge("A", "B", "is_a")
        self.kg.add_edge("C", "D", "is_a")
        self.kg.add_edge("E", "F", "has_a")
        edges = self.kg.get_edges_by_relation("is_a")
        self.assertEqual(len(edges), 2)

    # ---- 修改操作（软删除） ----

    def test_invalidate_node(self):
        """invalidate_node应将节点标记为无效"""
        node = self.kg.add_node("Python")
        self.assertTrue(node.is_valid)
        result = self.kg.invalidate_node(node.id)
        self.assertTrue(result)
        self.assertFalse(self.kg.get_node(node.id).is_valid)

    def test_invalidate_node_not_found(self):
        """invalidate_node对不存在的节点返回False"""
        self.assertFalse(self.kg.invalidate_node("nonexistent"))

    # ---- 删除操作 ----

    def test_remove_node(self):
        """remove_node应删除节点及其关联的边"""
        node = self.kg.add_node("Python")
        self.kg.add_edge("Python", "编程语言", "is_a")
        result = self.kg.remove_node(node.id)
        self.assertTrue(result)
        self.assertFalse(self.kg.node_exists(node.id))
        # 关联的边也应被删除
        self.assertEqual(len(self.kg.edges), 0)

    def test_remove_node_not_found(self):
        """remove_node对不存在的节点返回False"""
        self.assertFalse(self.kg.remove_node("nonexistent"))

    def test_remove_edge(self):
        """remove_edge应删除指定的边"""
        edge = self.kg.add_edge("A", "B", "关联")
        result = self.kg.remove_edge(edge.source_id, edge.target_id, "关联")
        self.assertTrue(result)
        self.assertEqual(len(self.kg.edges), 0)

    def test_remove_edge_not_found(self):
        """remove_edge对不存在的边返回False"""
        self.assertFalse(self.kg.remove_edge("x", "y", "不存在"))

    # ---- 统计 ----

    def test_get_stats_empty(self):
        """空图谱的统计应全为零"""
        stats = self.kg.get_stats()
        self.assertEqual(stats["total_nodes"], 0)
        self.assertEqual(stats["total_edges"], 0)
        self.assertEqual(stats["valid_nodes"], 0)
        self.assertEqual(stats["avg_weight"], 0.0)

    def test_get_stats_with_data(self):
        """有数据时统计应正确反映图谱状态"""
        self.kg.add_edge("A", "B", "r1", weight=0.5)
        self.kg.add_edge("C", "D", "r2", weight=0.9)
        stats = self.kg.get_stats()
        self.assertEqual(stats["total_nodes"], 4)
        self.assertEqual(stats["total_edges"], 2)
        self.assertEqual(stats["valid_nodes"], 4)
        self.assertEqual(stats["avg_weight"], 0.7)

    def test_get_stats_with_invalid_node(self):
        """无效节点应被排除在valid_nodes计数之外"""
        node = self.kg.add_node("A")
        self.kg.invalidate_node(node.id)
        stats = self.kg.get_stats()
        self.assertEqual(stats["total_nodes"], 1)
        self.assertEqual(stats["valid_nodes"], 0)


# ================================================================
# 阶段25: 持久化与重启恢复测试
# ================================================================

class TestKnowledgeGraphPersistence(unittest.TestCase):
    """验证知识图谱的持久化与重启恢复"""

    def setUp(self):
        """每个测试用例使用独立的临时目录"""
        self.tmp_dir = tempfile.mkdtemp()
        self.save_path = os.path.join(self.tmp_dir, "test_kg.json")

    def test_save_and_load(self):
        """保存后加载应完整恢复所有节点和边"""
        # 创建图谱并添加数据
        kg1 = KnowledgeGraph(save_path=self.save_path)
        node_a = kg1.add_node("Python", attr={"type": "语言"})
        node_b = kg1.add_node("编程语言")
        kg1.add_edge("Python", "编程语言", "is_a", weight=0.8)
        kg1.invalidate_node(node_a.id)
        kg1.save()

        # 重新加载
        kg2 = KnowledgeGraph(save_path=self.save_path)

        # 验证节点恢复
        self.assertEqual(len(kg2.nodes), 2)
        restored_a = kg2.get_node_by_name("Python")
        self.assertIsNotNone(restored_a)
        self.assertEqual(restored_a.id, node_a.id)
        self.assertEqual(restored_a.attributes, {"type": "语言"})
        self.assertFalse(restored_a.is_valid)

        # 验证边恢复
        self.assertEqual(len(kg2.edges), 1)
        edge = kg2.edges[0]
        self.assertEqual(edge.relation_name, "is_a")
        self.assertEqual(edge.weight, 0.8)

    def test_load_nonexistent_file(self):
        """加载不存在的文件应初始化为空图谱"""
        kg = KnowledgeGraph(save_path=self.save_path)
        self.assertEqual(len(kg.nodes), 0)
        self.assertEqual(len(kg.edges), 0)

    def test_persistence_after_restart(self):
        """模拟重启：创建->保存->销毁->重建->加载，数据应完整"""
        # 第一次启动
        kg1 = KnowledgeGraph(save_path=self.save_path)
        kg1.add_edge("人类", "哺乳动物", "is_a")
        kg1.add_edge("人类", "灵长目", "is_a")
        kg1.add_edge("Python", "编程语言", "is_a")
        stats_before = kg1.get_stats()
        kg1.save()
        del kg1

        # 第二次启动（模拟重启）
        kg2 = KnowledgeGraph(save_path=self.save_path)
        stats_after = kg2.get_stats()

        self.assertEqual(stats_before["total_nodes"], stats_after["total_nodes"])
        self.assertEqual(stats_before["total_edges"], stats_after["total_edges"])
        self.assertEqual(stats_before["valid_nodes"], stats_after["valid_nodes"])
        self.assertEqual(stats_before["avg_weight"], stats_after["avg_weight"])

    def test_save_creates_directory(self):
        """保存时应自动创建不存在的目录"""
        nested_path = os.path.join(self.tmp_dir, "sub", "dir", "kg.json")
        kg = KnowledgeGraph(save_path=nested_path)
        kg.add_node("测试")
        kg.save()
        self.assertTrue(os.path.exists(nested_path))

    def test_full_crud_lifecycle(self):
        """完整生命周期测试：创建->查询->修改->删除->持久化->恢复"""
        # 创建
        kg = KnowledgeGraph(save_path=self.save_path)
        kg.add_edge("A", "B", "关联", weight=0.6)
        kg.add_edge("B", "C", "依赖", weight=0.4)
        kg.add_edge("A", "C", "关联", weight=0.8)

        # 查询
        node_b = kg.get_node_by_name("B")
        self.assertIsNotNone(node_b)
        edges_from_b = kg.get_edges_by_source(node_b.id)
        self.assertEqual(len(edges_from_b), 1)

        # 修改（软删除）
        kg.invalidate_node(node_b.id)

        # 删除
        node_c = kg.get_node_by_name("C")
        node_a = kg.get_node_by_name("A")
        kg.remove_edge(node_a.id, node_c.id, "关联")

        # 持久化
        kg.save()

        # 恢复
        kg2 = KnowledgeGraph(save_path=self.save_path)
        self.assertEqual(kg2.get_stats()["total_nodes"], 3)
        self.assertEqual(kg2.get_stats()["total_edges"], 2)
        self.assertEqual(kg2.get_stats()["valid_nodes"], 2)
        self.assertFalse(kg2.get_node_by_name("B").is_valid)


if __name__ == "__main__":
    unittest.main()
