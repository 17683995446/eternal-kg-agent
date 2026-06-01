# -*- coding: utf-8 -*-
"""
永动知识图谱 Agent - 知识推演测试
阶段56-65: 知识推演与自驱
公理溯源: 自驱公理 - 测试验证推演逻辑的正确性，保障自驱机制的可靠性
"""

import os
import sys
import tempfile
import unittest

# 确保项目根目录在路径中
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.kg.knowledge_graph import KnowledgeGraph
from src.kg.task_deriver import TaskDeriver


class TestDeriveNewTasks(unittest.TestCase):
    """测试单跳推演。"""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.save_path = os.path.join(self.tmpdir, "kg.json")
        self.kg = KnowledgeGraph(save_path=self.save_path)

    def test_basic_derive(self):
        """基本推演：源节点有一条高权重边，应推演出目标任务。"""
        self.kg.add_edge("A", "B", "关联", weight=0.8)
        tasks = self.kg.derive_new_tasks("A", weight_threshold=0.2)
        self.assertEqual(tasks, ["知识推演任务:B"])

    def test_weight_filter(self):
        """权重过滤：低于阈值的边不应产生推演任务。"""
        self.kg.add_edge("A", "B", "关联", weight=0.1)
        tasks = self.kg.derive_new_tasks("A", weight_threshold=0.2)
        self.assertEqual(tasks, [])

    def test_dedup(self):
        """去重：同一目标节点只应出现一次。"""
        self.kg.add_edge("A", "B", "关联1", weight=0.5)
        self.kg.add_edge("A", "B", "关联2", weight=0.6)
        tasks = self.kg.derive_new_tasks("A")
        # B出现两次但应去重为一次
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0], "知识推演任务:B")

    def test_nonexistent_node(self):
        """不存在的节点应返回空列表。"""
        tasks = self.kg.derive_new_tasks("不存在")
        self.assertEqual(tasks, [])

    def test_multiple_targets(self):
        """多目标推演。"""
        self.kg.add_edge("A", "B", "关联", weight=0.5)
        self.kg.add_edge("A", "C", "关联", weight=0.7)
        tasks = self.kg.derive_new_tasks("A")
        self.assertEqual(len(tasks), 2)
        self.assertIn("知识推演任务:B", tasks)
        self.assertIn("知识推演任务:C", tasks)


class TestDeriveMultiHopTasks(unittest.TestCase):
    """测试多跳推演。"""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.save_path = os.path.join(self.tmpdir, "kg.json")
        self.kg = KnowledgeGraph(save_path=self.save_path)

    def test_two_hop(self):
        """二跳推演：A->B->C，应推演出B和C。"""
        self.kg.add_edge("A", "B", "关联", weight=0.8)
        self.kg.add_edge("B", "C", "关联", weight=0.8)
        tasks = self.kg.derive_multi_hop_tasks("A", max_hops=2)
        self.assertIn("知识推演任务:B", tasks)
        self.assertIn("知识推演任务:C", tasks)

    def test_one_hop_only(self):
        """限制一跳时不应推演出二跳目标。"""
        self.kg.add_edge("A", "B", "关联", weight=0.8)
        self.kg.add_edge("B", "C", "关联", weight=0.8)
        tasks = self.kg.derive_multi_hop_tasks("A", max_hops=1)
        self.assertIn("知识推演任务:B", tasks)
        self.assertNotIn("知识推演任务:C", tasks)

    def test_two_hop_weight_filter(self):
        """二跳中低权重边不应产生推演。"""
        self.kg.add_edge("A", "B", "关联", weight=0.8)
        self.kg.add_edge("B", "C", "关联", weight=0.05)
        tasks = self.kg.derive_multi_hop_tasks("A", max_hops=2,
                                               weight_threshold=0.2)
        self.assertIn("知识推演任务:B", tasks)
        self.assertNotIn("知识推演任务:C", tasks)

    def test_two_hop_dedup(self):
        """二跳去重：如果C同时是第一跳和第二跳目标，只应出现一次。"""
        self.kg.add_edge("A", "C", "关联", weight=0.8)
        self.kg.add_edge("A", "B", "关联", weight=0.8)
        self.kg.add_edge("B", "C", "关联", weight=0.8)
        tasks = self.kg.derive_multi_hop_tasks("A", max_hops=2)
        c_count = tasks.count("知识推演任务:C")
        self.assertEqual(c_count, 1)


class TestDeriveFrequencyControl(unittest.TestCase):
    """测试推演频率控制。"""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.save_path = os.path.join(self.tmpdir, "kg.json")
        self.kg = KnowledgeGraph(save_path=self.save_path)

    def test_frequency_control(self):
        """同一节点不应被重复推演。"""
        freq = self.kg.get_derive_frequency_control()
        self.assertFalse("A" in freq)
        freq.add("A")
        self.assertTrue("A" in freq)

    def test_frequency_control_persistent(self):
        """频率控制集合应在多次调用间保持。"""
        freq1 = self.kg.get_derive_frequency_control()
        freq1.add("X")
        freq2 = self.kg.get_derive_frequency_control()
        self.assertTrue("X" in freq2)


class TestTaskDeriver(unittest.TestCase):
    """测试TaskDeriver综合推演。"""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.save_path = os.path.join(self.tmpdir, "kg.json")
        self.kg = KnowledgeGraph(save_path=self.save_path)
        self.deriver = TaskDeriver(self.kg)

    def test_derive_from_task(self):
        """综合推演应返回Task对象列表。"""
        self.kg.add_edge("知识A", "知识B", "关联", weight=0.8)
        tasks = self.deriver.derive_from_task("知识A")
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].name, "知识推演任务:知识B")
        self.assertIsInstance(tasks[0].priority, int)
        self.assertGreater(tasks[0].priority, 0)

    def test_priority_mapping(self):
        """高权重边应映射为高优先级。"""
        self.kg.add_edge("A", "B", "关联", weight=0.9)
        self.kg.add_edge("A", "C", "关联", weight=0.3)
        tasks = self.deriver.derive_from_task("A")
        # 按优先级降序排列，B的优先级应高于C
        priorities = [t.priority for t in tasks]
        self.assertEqual(priorities, sorted(priorities, reverse=True))

    def test_frequency_skip(self):
        """已推演节点应被跳过。"""
        self.kg.add_edge("A", "B", "关联", weight=0.8)
        tasks1 = self.deriver.derive_from_task("A")
        self.assertEqual(len(tasks1), 1)
        # 第二次推演应被频率控制跳过
        tasks2 = self.deriver.derive_from_task("A")
        self.assertEqual(len(tasks2), 0)

    def test_empty_derive(self):
        """无关联节点应返回空列表。"""
        self.kg.add_node("孤立节点")
        tasks = self.deriver.derive_from_task("孤立节点")
        self.assertEqual(tasks, [])


if __name__ == "__main__":
    unittest.main()
