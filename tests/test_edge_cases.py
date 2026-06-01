# -*- coding: utf-8 -*-
"""
永动知识图谱 Agent - 边界条件与异常注入测试
阶段98: 测试空图谱操作、超大名称、极端权重、并发IO、损坏文件恢复、空队列
公理溯源: 存续公理 - 边界测试验证系统在极端条件下的存续能力
设计原则: 覆盖所有已知边界场景，确保系统健壮性
"""

import json
import os
import sys
import tempfile
import time
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.kg.evolution import KnowledgeEvolution
from src.kg.knowledge_graph import KnowledgeGraph
from src.kg.task_deriver import TaskDeriver
from src.task.task import Task
from src.task.task_queue import TaskQueue


class TestEmptyGraphOperations(unittest.TestCase):
    """空图谱操作：推演、进化、统计。"""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.save_path = os.path.join(self.tmp_dir, "empty_kg.json")
        self.kg = KnowledgeGraph(save_path=self.save_path)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_derive_on_empty_graph(self):
        """空图谱推演应返回空列表。"""
        tasks = self.kg.derive_new_tasks("不存在的节点")
        self.assertEqual(tasks, [])

    def test_multi_hop_derive_on_empty_graph(self):
        """空图谱多跳推演应返回空列表。"""
        tasks = self.kg.derive_multi_hop_tasks("不存在的节点")
        self.assertEqual(tasks, [])

    def test_evolve_on_empty_graph(self):
        """空图谱进化不应报错。"""
        backup_dir = os.path.join(self.tmp_dir, "backups")
        evolution = KnowledgeEvolution(self.kg)
        report = evolution.evolve(backup_dir=backup_dir)
        self.assertTrue(report["evolution_success"])
        self.assertEqual(report["before"]["total_nodes"], 0)
        self.assertEqual(report["after"]["total_nodes"], 0)

    def test_stats_on_empty_graph(self):
        """空图谱统计应返回零值。"""
        stats = self.kg.get_stats()
        self.assertEqual(stats["total_nodes"], 0)
        self.assertEqual(stats["total_edges"], 0)
        self.assertEqual(stats["valid_nodes"], 0)
        self.assertEqual(stats["avg_weight"], 0.0)

    def test_evolution_report_on_empty_graph(self):
        """空图谱进化报告应返回零值。"""
        report = self.kg.get_evolution_report()
        self.assertEqual(report["total_nodes"], 0)
        self.assertEqual(report["total_edges"], 0)
        self.assertEqual(report["valid_nodes"], 0)
        self.assertEqual(report["avg_weight"], 0.0)

    def test_trim_on_empty_graph(self):
        """空图谱修剪不应报错。"""
        result = self.kg.trim_invalid_knowledge()
        self.assertEqual(result["edges_removed"], 0)
        self.assertEqual(result["nodes_removed"], 0)

    def test_decay_on_empty_graph(self):
        """空图谱衰减不应报错。"""
        self.kg.decay_edges(0.95)
        self.assertEqual(len(self.kg.edges), 0)

    def test_normalize_on_empty_graph(self):
        """空图谱归一化不应报错。"""
        self.kg.normalize_weights()
        self.assertEqual(len(self.kg.edges), 0)

    def test_task_deriver_on_empty_graph(self):
        """空图谱上TaskDeriver不应报错。"""
        deriver = TaskDeriver(self.kg)
        tasks = deriver.derive_from_task("不存在的节点")
        self.assertEqual(tasks, [])

    def test_save_and_load_empty_graph(self):
        """空图谱保存和加载应正常工作。"""
        self.kg.save()
        kg2 = KnowledgeGraph(save_path=self.save_path)
        self.assertEqual(len(kg2.nodes), 0)
        self.assertEqual(len(kg2.edges), 0)


class TestLargeNames(unittest.TestCase):
    """超大任务名/节点名测试。"""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.save_path = os.path.join(self.tmp_dir, "large_kg.json")
        self.kg = KnowledgeGraph(save_path=self.save_path)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_large_node_name(self):
        """超大节点名应正常处理。"""
        large_name = "节点_" + "A" * 10000
        node = self.kg.add_node(large_name)
        self.assertEqual(node.name, large_name)
        found = self.kg.get_node_by_name(large_name)
        self.assertIsNotNone(found)

    def test_large_task_name(self):
        """超大任务名应正常入队。"""
        large_name = "任务_" + "B" * 10000
        task = Task(name=large_name)
        queue = self._create_test_queue()
        result = queue.add_task(task)
        self.assertTrue(result)
        got = queue.get_task()
        self.assertEqual(got.name, large_name)

    def test_large_name_persistence(self):
        """超大名称应能正常持久化和恢复。"""
        large_name = "持久化_" + "C" * 5000
        self.kg.add_node(large_name)
        self.kg.add_edge(large_name, "目标", "关联")
        self.kg.save()

        kg2 = KnowledgeGraph(save_path=self.save_path)
        found = kg2.get_node_by_name(large_name)
        self.assertIsNotNone(found)

    def _create_test_queue(self):
        """创建使用临时路径的TaskQueue。"""
        tq_path = os.path.join(self.tmp_dir, f"tq_{time.time_ns()}.json")
        import src.task.task_queue as tq_module
        import src.config as cfg_module
        orig = cfg_module.TASK_QUEUE_SAVE_PATH
        cfg_module.TASK_QUEUE_SAVE_PATH = tq_path
        tq_module.TASK_QUEUE_SAVE_PATH = tq_path
        queue = TaskQueue(max_size=200)
        cfg_module.TASK_QUEUE_SAVE_PATH = orig
        tq_module.TASK_QUEUE_SAVE_PATH = orig
        return queue


class TestExtremeWeights(unittest.TestCase):
    """权重为0和负值的边界测试。"""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.save_path = os.path.join(self.tmp_dir, "weight_kg.json")
        self.kg = KnowledgeGraph(save_path=self.save_path)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_zero_weight_edge(self):
        """权重为0的边应正常创建。"""
        edge = self.kg.add_edge("A", "B", "关联", weight=0.0)
        self.assertEqual(edge.weight, 0.0)

    def test_zero_weight_not_derived(self):
        """权重为0的边不应被推演（默认阈值0.2）。"""
        self.kg.add_edge("A", "B", "关联", weight=0.0)
        tasks = self.kg.derive_new_tasks("A")
        self.assertEqual(tasks, [])

    def test_negative_weight_edge(self):
        """负权重边应正常创建（系统不校验范围）。"""
        edge = self.kg.add_edge("A", "B", "关联", weight=-0.5)
        self.assertEqual(edge.weight, -0.5)

    def test_negative_weight_not_derived(self):
        """负权重边不应被推演。"""
        self.kg.add_edge("A", "B", "关联", weight=-0.5)
        tasks = self.kg.derive_new_tasks("A")
        self.assertEqual(tasks, [])

    def test_weight_above_one(self):
        """超过1.0的权重应正常创建。"""
        edge = self.kg.add_edge("A", "B", "关联", weight=2.0)
        self.assertEqual(edge.weight, 2.0)

    def test_normalize_with_negative_weights(self):
        """含负权重时归一化不应报错。"""
        self.kg.add_edge("A", "B", "r1", weight=-0.5)
        self.kg.add_edge("A", "C", "r2", weight=0.5)
        # 最大权重为0.5，归一化后-0.5变为-1.0，0.5变为1.0
        self.kg.normalize_weights()
        self.assertAlmostEqual(self.kg.edges[0].weight, -1.0, places=4)
        self.assertAlmostEqual(self.kg.edges[1].weight, 1.0, places=4)

    def test_trim_with_zero_weight(self):
        """权重为0的边在trim_threshold=0.1时应被删除。"""
        self.kg.add_edge("A", "B", "r1", weight=0.0)
        self.kg.add_edge("A", "C", "r2", weight=0.5)
        result = self.kg.trim_invalid_knowledge(weight_threshold=0.1)
        self.assertEqual(result["edges_removed"], 1)
        self.assertEqual(len(self.kg.edges), 1)


class TestRapidSaveLoad(unittest.TestCase):
    """并发保存/加载（快速连续操作）测试。"""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.save_path = os.path.join(self.tmp_dir, "rapid_kg.json")

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_rapid_save_load_cycles(self):
        """快速连续save/load不应导致数据损坏。"""
        kg = KnowledgeGraph(save_path=self.save_path)
        kg.add_edge("A", "B", "关联", weight=0.5)

        for i in range(100):
            kg.save()
            kg.load()
            # 每次load后验证数据
            self.assertEqual(len(kg.nodes), 2)
            self.assertEqual(len(kg.edges), 1)

    def test_rapid_save_with_updates(self):
        """快速连续save并更新数据。"""
        kg = KnowledgeGraph(save_path=self.save_path)
        for i in range(100):
            kg.add_node(f"rapid_{i}")
            kg.save()

        # 重新加载验证
        kg2 = KnowledgeGraph(save_path=self.save_path)
        self.assertEqual(len(kg2.nodes), 100)


class TestCorruptedJsonRecovery(unittest.TestCase):
    """损坏的JSON文件恢复测试。"""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.save_path = os.path.join(self.tmp_dir, "corrupt_kg.json")

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_corrupted_json_kg_load(self):
        """损坏的JSON文件加载时应使用空图谱，不应崩溃。"""
        # 写入损坏的JSON
        with open(self.save_path, "w", encoding="utf-8") as f:
            f.write("{corrupted json content!!!")

        kg = KnowledgeGraph(save_path=self.save_path)
        self.assertEqual(len(kg.nodes), 0)
        self.assertEqual(len(kg.edges), 0)

    def test_empty_json_kg_load(self):
        """空JSON文件加载时应使用空图谱。"""
        with open(self.save_path, "w", encoding="utf-8") as f:
            f.write("")

        kg = KnowledgeGraph(save_path=self.save_path)
        self.assertEqual(len(kg.nodes), 0)

    def test_partial_json_kg_load(self):
        """部分有效的JSON加载时应尽可能恢复。"""
        # 写入缺少必要字段的JSON
        data = {"nodes": [{"id": "n1"}], "edges": []}
        with open(self.save_path, "w", encoding="utf-8") as f:
            json.dump(data, f)

        # 缺少name字段应导致加载失败，使用空图谱
        kg = KnowledgeGraph(save_path=self.save_path)
        # 系统应优雅处理，不崩溃
        self.assertIsInstance(kg.nodes, dict)

    def test_corrupted_json_task_queue_load(self):
        """损坏的JSON文件加载任务队列时应使用空队列。"""
        tq_path = os.path.join(self.tmp_dir, "corrupt_tq.json")
        import src.task.task_queue as tq_module
        import src.config as cfg_module
        orig = cfg_module.TASK_QUEUE_SAVE_PATH
        cfg_module.TASK_QUEUE_SAVE_PATH = tq_path
        tq_module.TASK_QUEUE_SAVE_PATH = tq_path

        with open(tq_path, "w", encoding="utf-8") as f:
            f.write("{{invalid json")

        queue = TaskQueue(max_size=10)
        self.assertTrue(queue.is_empty())

        cfg_module.TASK_QUEUE_SAVE_PATH = orig
        tq_module.TASK_QUEUE_SAVE_PATH = orig

    def test_binary_content_kg_load(self):
        """二进制内容文件加载时应使用空图谱。"""
        with open(self.save_path, "wb") as f:
            f.write(b"\x00\x01\x02\x03\xff\xfe")

        kg = KnowledgeGraph(save_path=self.save_path)
        self.assertEqual(len(kg.nodes), 0)


class TestEmptyQueueOperations(unittest.TestCase):
    """空队列操作测试。"""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_get_from_empty_queue(self):
        """空队列get_task应返回None。"""
        queue = self._create_test_queue()
        self.assertIsNone(queue.get_task())

    def test_peek_empty_queue(self):
        """空队列peek应返回None。"""
        queue = self._create_test_queue()
        self.assertIsNone(queue.peek())

    def test_is_empty_true(self):
        """空队列is_empty应返回True。"""
        queue = self._create_test_queue()
        self.assertTrue(queue.is_empty())

    def test_size_zero(self):
        """空队列size应为0。"""
        queue = self._create_test_queue()
        self.assertEqual(queue.size, 0)

    def test_clear_empty_queue(self):
        """清空空队列不应报错。"""
        queue = self._create_test_queue()
        queue.clear()
        self.assertTrue(queue.is_empty())

    def test_save_empty_queue(self):
        """保存空队列不应报错。"""
        queue = self._create_test_queue()
        queue.save()

    def test_batch_add_empty_list(self):
        """批量添加空列表应返回0。"""
        queue = self._create_test_queue()
        count = queue.batch_add_tasks([])
        self.assertEqual(count, 0)

    def test_multiple_gets_from_empty(self):
        """多次从空队列获取应始终返回None。"""
        queue = self._create_test_queue()
        for _ in range(10):
            self.assertIsNone(queue.get_task())

    def _create_test_queue(self):
        """创建使用临时路径的TaskQueue。"""
        tq_path = os.path.join(self.tmp_dir, f"tq_{time.time_ns()}.json")
        import src.task.task_queue as tq_module
        import src.config as cfg_module
        orig = cfg_module.TASK_QUEUE_SAVE_PATH
        cfg_module.TASK_QUEUE_SAVE_PATH = tq_path
        tq_module.TASK_QUEUE_SAVE_PATH = tq_path
        queue = TaskQueue(max_size=200)
        cfg_module.TASK_QUEUE_SAVE_PATH = orig
        tq_module.TASK_QUEUE_SAVE_PATH = orig
        return queue


class TestSpecialCharacters(unittest.TestCase):
    """特殊字符和Unicode名称测试。"""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.save_path = os.path.join(self.tmp_dir, "special_kg.json")
        self.kg = KnowledgeGraph(save_path=self.save_path)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_unicode_node_name(self):
        """Unicode节点名应正常处理。"""
        names = ["节点Alpha", "ノードBeta", "УзелGamma", "مرکزDelta"]
        for name in names:
            node = self.kg.add_node(name)
            self.assertEqual(node.name, name)

    def test_special_characters_in_name(self):
        """包含特殊字符的名称应正常处理。"""
        names = ["a<b>c", "a&b", "a\"b", "a'b", "a\\b", "a/b"]
        for name in names:
            node = self.kg.add_node(name)
            self.assertEqual(node.name, name)
            found = self.kg.get_node_by_name(name)
            self.assertIsNotNone(found)

    def test_whitespace_name(self):
        """纯空白名称应正常处理。"""
        node = self.kg.add_node("   ")
        self.assertEqual(node.name, "   ")

    def test_empty_string_name(self):
        """空字符串名称应正常处理。"""
        node = self.kg.add_node("")
        self.assertEqual(node.name, "")


if __name__ == "__main__":
    unittest.main()
