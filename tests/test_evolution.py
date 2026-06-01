# -*- coding: utf-8 -*-
"""
永动知识图谱 Agent - 知识进化测试
阶段66-75: 知识进化与精简
公理溯源: 自驱公理 - 测试验证进化流程的正确性，保障知识自我优化机制的可靠性
"""

import os
import sys
import tempfile
import unittest

# 确保项目根目录在路径中
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.kg.evolution import KnowledgeEvolution
from src.kg.knowledge_graph import KnowledgeGraph


class TestDecayEdges(unittest.TestCase):
    """测试边权重衰减。"""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.save_path = os.path.join(self.tmpdir, "kg.json")
        self.kg = KnowledgeGraph(save_path=self.save_path)

    def test_decay(self):
        """衰减后所有边权重应乘以衰减系数。"""
        self.kg.add_edge("A", "B", "关联", weight=1.0)
        self.kg.add_edge("B", "C", "关联", weight=0.5)
        self.kg.decay_edges(0.5)
        weights = [e.weight for e in self.kg.edges]
        self.assertAlmostEqual(weights[0], 0.5, places=4)
        self.assertAlmostEqual(weights[1], 0.25, places=4)

    def test_decay_no_edges(self):
        """无边的图谱衰减不应报错。"""
        self.kg.decay_edges(0.95)
        self.assertEqual(len(self.kg.edges), 0)


class TestTrimInvalidKnowledge(unittest.TestCase):
    """测试修剪无效知识。"""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.save_path = os.path.join(self.tmpdir, "kg.json")
        self.kg = KnowledgeGraph(save_path=self.save_path)

    def test_trim_low_weight_edges(self):
        """低权重边应被删除。"""
        self.kg.add_edge("A", "B", "关联", weight=0.05)
        self.kg.add_edge("A", "C", "关联", weight=0.5)
        result = self.kg.trim_invalid_knowledge(weight_threshold=0.1)
        self.assertEqual(result["edges_removed"], 1)
        self.assertEqual(len(self.kg.edges), 1)

    def test_trim_orphan_nodes(self):
        """孤立节点应被清理。"""
        self.kg.add_node("孤立节点")
        self.kg.add_edge("A", "B", "关联", weight=0.5)
        result = self.kg.trim_invalid_knowledge(weight_threshold=0.0)
        # "孤立节点"无任何边，应被清理
        self.assertEqual(result["nodes_removed"], 1)
        self.assertIsNone(self.kg.get_node_by_name("孤立节点"))

    def test_trim_preserves_connected(self):
        """有边连接的节点不应被清理。"""
        self.kg.add_edge("A", "B", "关联", weight=0.5)
        self.kg.trim_invalid_knowledge(weight_threshold=0.0)
        self.assertIsNotNone(self.kg.get_node_by_name("A"))
        self.assertIsNotNone(self.kg.get_node_by_name("B"))


class TestStrengthenEdge(unittest.TestCase):
    """测试边权重增强。"""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.save_path = os.path.join(self.tmpdir, "kg.json")
        self.kg = KnowledgeGraph(save_path=self.save_path)

    def test_strengthen(self):
        """增强后权重应增加。"""
        self.kg.add_edge("A", "B", "关联", weight=0.5)
        result = self.kg.strengthen_edge("A", "B", "关联", boost=0.2)
        self.assertTrue(result)
        edge = self.kg.edges[0]
        self.assertAlmostEqual(edge.weight, 0.7, places=4)

    def test_strengthen_cap(self):
        """增强后权重不应超过1.0。"""
        self.kg.add_edge("A", "B", "关联", weight=0.95)
        self.kg.strengthen_edge("A", "B", "关联", boost=0.2)
        edge = self.kg.edges[0]
        self.assertAlmostEqual(edge.weight, 1.0, places=4)

    def test_strengthen_nonexistent(self):
        """不存在的边应返回False。"""
        result = self.kg.strengthen_edge("X", "Y", "关联")
        self.assertFalse(result)


class TestNormalizeWeights(unittest.TestCase):
    """测试权重归一化。"""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.save_path = os.path.join(self.tmpdir, "kg.json")
        self.kg = KnowledgeGraph(save_path=self.save_path)

    def test_normalize(self):
        """归一化后最大权重应为1.0。"""
        self.kg.add_edge("A", "B", "关联", weight=0.4)
        self.kg.add_edge("B", "C", "关联", weight=0.8)
        self.kg.normalize_weights()
        max_w = max(e.weight for e in self.kg.edges)
        self.assertAlmostEqual(max_w, 1.0, places=4)

    def test_normalize_no_edges(self):
        """无边的图谱归一化不应报错。"""
        self.kg.normalize_weights()
        self.assertEqual(len(self.kg.edges), 0)

    def test_normalize_zero_weights(self):
        """所有权重为0时归一化不应报错。"""
        self.kg.add_edge("A", "B", "关联", weight=0.0)
        self.kg.normalize_weights()
        self.assertAlmostEqual(self.kg.edges[0].weight, 0.0, places=4)


class TestBackupGraph(unittest.TestCase):
    """测试图谱备份。"""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.save_path = os.path.join(self.tmpdir, "kg.json")
        self.backup_dir = os.path.join(self.tmpdir, "backups")
        self.kg = KnowledgeGraph(save_path=self.save_path)

    def test_backup(self):
        """备份应创建文件。"""
        self.kg.add_edge("A", "B", "关联", weight=0.5)
        self.kg.save()
        path = self.kg.backup_graph(backup_dir=self.backup_dir)
        self.assertIsNotNone(path)
        self.assertTrue(os.path.exists(path))

    def test_backup_nonexistent_file(self):
        """图谱文件不存在时应返回None。"""
        # 创建一个不存在的save_path
        kg = KnowledgeGraph(save_path="/nonexistent/path/kg.json")
        path = kg.backup_graph(backup_dir=self.backup_dir)
        self.assertIsNone(path)

    def test_max_backups(self):
        """备份数量不应超过max_backups。"""
        self.kg.save()
        for i in range(8):
            path = self.kg.backup_graph(backup_dir=self.backup_dir,
                                         max_backups=5)
            self.assertIsNotNone(path)
        backups = [f for f in os.listdir(self.backup_dir)
                   if f.startswith("kg_backup_")]
        self.assertLessEqual(len(backups), 5)


class TestEvolutionReport(unittest.TestCase):
    """测试进化报告。"""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.save_path = os.path.join(self.tmpdir, "kg.json")
        self.kg = KnowledgeGraph(save_path=self.save_path)

    def test_report(self):
        """进化报告应包含正确的统计信息。"""
        self.kg.add_edge("A", "B", "关联", weight=0.5)
        report = self.kg.get_evolution_report()
        self.assertEqual(report["total_nodes"], 2)
        self.assertEqual(report["total_edges"], 1)
        self.assertEqual(report["valid_nodes"], 2)

    def test_empty_report(self):
        """空图谱报告应返回零值。"""
        report = self.kg.get_evolution_report()
        self.assertEqual(report["total_nodes"], 0)
        self.assertEqual(report["total_edges"], 0)
        self.assertEqual(report["avg_weight"], 0.0)


class TestKnowledgeEvolution(unittest.TestCase):
    """测试完整进化周期。"""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.save_path = os.path.join(self.tmpdir, "kg.json")
        self.backup_dir = os.path.join(self.tmpdir, "backups")
        self.kg = KnowledgeGraph(save_path=self.save_path)
        self.evolution = KnowledgeEvolution(self.kg)

    def test_full_evolution_cycle(self):
        """完整进化周期应执行衰减、修剪、归一化、备份。"""
        self.kg.add_edge("A", "B", "关联", weight=0.9)
        self.kg.add_edge("A", "C", "关联", weight=0.05)
        self.kg.add_edge("B", "D", "关联", weight=0.7)

        report = self.evolution.evolve(
            decay_factor=0.5,
            trim_threshold=0.1,
            backup_dir=self.backup_dir,
        )

        self.assertTrue(report["evolution_success"])
        self.assertIn("before", report)
        self.assertIn("after", report)
        self.assertIn("trim", report)
        self.assertIsNotNone(report["backup_path"])
        # 低权重边应在衰减后被修剪
        self.assertLessEqual(report["after"]["total_edges"],
                             report["before"]["total_edges"])

    def test_evolution_backup_created(self):
        """进化后应创建备份文件。"""
        self.kg.add_edge("A", "B", "关联", weight=0.5)
        self.evolution.evolve(backup_dir=self.backup_dir)
        backups = [f for f in os.listdir(self.backup_dir)
                   if f.startswith("kg_backup_")]
        self.assertGreaterEqual(len(backups), 1)


if __name__ == "__main__":
    unittest.main()
