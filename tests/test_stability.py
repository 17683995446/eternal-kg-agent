# -*- coding: utf-8 -*-
"""
永动知识图谱 Agent - 长时间稳定性测试
阶段97: 模拟连续运行，验证无异常、无内存泄漏、数据一致性
公理溯源: 存续公理 - 稳定性测试验证系统长时间存续的可靠性
设计原则: 使用unittest，通过对象计数验证无内存泄漏，通过数据校验验证一致性
"""

import gc
import os
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.agent.agent import EternalSelfAgent
from src.kg.evolution import KnowledgeEvolution
from src.kg.knowledge_graph import KnowledgeGraph
from src.task.task import Task


class TestStabilityLoopIterations(unittest.TestCase):
    """模拟1000次循环迭代，验证无异常。"""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_1000_loop_iterations(self):
        """执行1000次循环迭代，验证无异常且系统状态正常。"""
        agent = EternalSelfAgent(base_dir=self.tmp_dir)
        agent.task_queue.add_task(Task(name="稳定性测试任务"))

        iteration_count = [0]

        def controlled_sleep(duration):
            iteration_count[0] += 1
            if iteration_count[0] >= 1000:
                agent.system_alive = False

        with patch("src.agent.agent.time.sleep", side_effect=controlled_sleep):
            agent.eternal_loop()

        # 验证：循环正常完成
        self.assertGreaterEqual(agent.run_counter, 1)
        self.assertGreaterEqual(iteration_count[0], 1000)

        # 验证：图谱数据一致
        stats = agent.knowledge_graph.get_stats()
        self.assertGreater(stats["total_nodes"], 0)
        self.assertGreater(stats["total_edges"], 0)

        # 验证：无未捕获异常导致的状态损坏
        self.assertTrue(agent.system_alive is False or agent.run_counter > 0)


class TestStabilityTaskExecution(unittest.TestCase):
    """执行500次任务（自动产生新任务），验证无异常。"""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_500_task_executions(self):
        """执行500次任务，验证队列和图谱状态一致。"""
        agent = EternalSelfAgent(base_dir=self.tmp_dir)

        # 预注入足够多的任务
        for i in range(500):
            agent.task_queue.add_task(Task(name=f"批量任务_{i}"))

        stop_count = [0]

        def controlled_sleep(duration):
            stop_count[0] += 1
            if agent.run_counter >= 500:
                agent.system_alive = False

        with patch("src.agent.agent.time.sleep", side_effect=controlled_sleep):
            agent.eternal_loop()

        # 验证：至少执行了500个任务
        self.assertGreaterEqual(agent.run_counter, 500)

        # 验证：图谱中有对应的节点
        stats = agent.knowledge_graph.get_stats()
        self.assertGreater(stats["total_nodes"], 0)

        # 验证：有"自主衍生"边
        edges = agent.knowledge_graph.get_edges_by_relation("自主衍生")
        self.assertGreater(len(edges), 0)


class TestStabilityEvolutionCycles(unittest.TestCase):
    """执行20次进化周期，验证无异常。"""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.save_path = os.path.join(self.tmp_dir, "kg.json")
        self.backup_dir = os.path.join(self.tmp_dir, "backups")

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_20_evolution_cycles(self):
        """执行20次进化周期，验证每次都成功且数据一致。"""
        kg = KnowledgeGraph(save_path=self.save_path)

        # 构建初始图谱
        for i in range(50):
            kg.add_edge(f"节点_{i}", f"节点_{(i+1)%50}", "关联", weight=0.8)
            kg.add_edge(f"节点_{i}", f"节点_{(i+2)%50}", "依赖", weight=0.6)

        evolution = KnowledgeEvolution(kg)

        for cycle in range(20):
            report = evolution.evolve(
                decay_factor=0.95,
                trim_threshold=0.05,
                backup_dir=self.backup_dir,
                max_backups=5,
            )
            self.assertTrue(report["evolution_success"])

        # 验证：最终图谱状态有效
        stats = kg.get_stats()
        self.assertGreater(stats["total_nodes"], 0)
        self.assertGreater(stats["total_edges"], 0)

        # 验证：备份数量不超过限制
        backups = [f for f in os.listdir(self.backup_dir)
                   if f.startswith("kg_backup_")]
        self.assertLessEqual(len(backups), 5)


class TestStabilityMemoryLeak(unittest.TestCase):
    """通过统计对象数量验证无内存泄漏。"""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.save_path = os.path.join(self.tmp_dir, "kg.json")

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_no_memory_leak_in_kg_operations(self):
        """反复创建/销毁图谱，验证Node/Edge对象无泄漏。"""
        gc.collect()
        before_count = len(gc.get_objects())

        for _ in range(100):
            kg = KnowledgeGraph(save_path=self.save_path)
            for i in range(50):
                kg.add_edge(f"n_{i}", f"n_{(i+1)%50}", "r", weight=0.5)
            kg.get_stats()
            kg.derive_new_tasks("n_0")
            kg.save()
            del kg

        gc.collect()
        after_count = len(gc.get_objects())

        # 对象增长应在合理范围内（允许一定波动）
        growth = after_count - before_count
        self.assertLess(growth, 5000,
                         f"对象增长{growth}过多，可能存在内存泄漏")

    def test_no_memory_leak_in_task_operations(self):
        """反复创建/销毁任务队列，验证Task对象无泄漏。"""
        gc.collect()
        before_count = len(gc.get_objects())

        for _ in range(100):
            queue = self._create_test_queue()
            for i in range(50):
                queue.add_task(Task(name=f"task_{i}"))
            for _ in range(50):
                queue.get_task()
            del queue

        gc.collect()
        after_count = len(gc.get_objects())

        growth = after_count - before_count
        self.assertLess(growth, 5000,
                         f"对象增长{growth}过多，可能存在内存泄漏")

    def _create_test_queue(self):
        """创建使用临时路径的TaskQueue。"""
        from src.task.task_queue import TaskQueue
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


class TestStabilityDataConsistency(unittest.TestCase):
    """验证长时间运行后数据一致性。"""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.save_path = os.path.join(self.tmp_dir, "kg.json")

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_graph_consistency_after_many_operations(self):
        """大量增删操作后，图谱内部索引应保持一致。"""
        kg = KnowledgeGraph(save_path=self.save_path)

        # 大量添加
        for i in range(200):
            kg.add_node(f"consist_{i}")
            kg.add_edge(f"consist_{i}", f"consist_{(i+1)%200}", "关联")

        # 部分删除
        for i in range(0, 200, 4):
            node = kg.get_node_by_name(f"consist_{i}")
            if node:
                kg.remove_node(node.id)

        # 验证：名称索引与节点字典一致
        for name, nid in kg._name_index.items():
            self.assertIn(nid, kg.nodes, f"名称索引中的{name}指向不存在的节点{nid}")
            self.assertEqual(kg.nodes[nid].name, name,
                             f"节点{nid}的名称{name}与索引不匹配")

        # 验证：所有边的源和目标节点都存在
        for edge in kg.edges:
            self.assertIn(edge.source_id, kg.nodes,
                          f"边引用了不存在的源节点{edge.source_id}")
            self.assertIn(edge.target_id, kg.nodes,
                          f"边引用了不存在的目标节点{edge.target_id}")

        # 验证：save/load后一致性保持
        kg.save()
        kg2 = KnowledgeGraph(save_path=self.save_path)
        self.assertEqual(len(kg2.nodes), len(kg.nodes))
        self.assertEqual(len(kg2.edges), len(kg.edges))


if __name__ == "__main__":
    unittest.main()
