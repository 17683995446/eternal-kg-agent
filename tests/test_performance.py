# -*- coding: utf-8 -*-
"""
永动知识图谱 Agent - 性能优化与基准测试
阶段96: 测试不同图谱规模下的操作耗时，输出基准报告
公理溯源: 存续公理 - 性能基准是衡量系统存续效率的量化依据
设计原则: 使用time模块计时，覆盖100/1000/10000节点规模，仅使用标准库
"""

import os
import sys
import tempfile
import time
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.kg.knowledge_graph import KnowledgeGraph
from src.task.task import Task


class PerformanceBenchmark(unittest.TestCase):
    """性能基准测试：测量不同图谱规模下的操作耗时。"""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.save_path = os.path.join(self.tmp_dir, "bench_kg.json")

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    # ================================================================
    # 辅助方法：构建指定规模的图谱
    # ================================================================

    def _build_graph(self, kg, num_nodes, edges_per_node=2):
        """构建指定节点数的图谱，每个节点连接edges_per_node条边。"""
        for i in range(num_nodes):
            kg.add_node(f"node_{i}")
        # 添加边：每个节点连接后续若干节点
        for i in range(num_nodes):
            for j in range(1, edges_per_node + 1):
                target = (i + j) % num_nodes
                kg.add_edge(f"node_{i}", f"node_{target}", f"rel_{j}", weight=0.5)

    # ================================================================
    # add_node / add_edge 操作耗时
    # ================================================================

    def test_add_node_performance(self):
        """测试不同规模下add_node操作的耗时。"""
        for scale in [100, 1000]:
            kg = KnowledgeGraph(save_path=self.save_path)
            start = time.perf_counter()
            for i in range(scale):
                kg.add_node(f"perf_node_{i}")
            elapsed = time.perf_counter() - start
            avg_ms = (elapsed / scale) * 1000
            # 100节点应在合理时间内完成
            self.assertLess(elapsed, 5.0, f"add_node {scale}节点耗时{elapsed:.3f}s过长")

    def test_add_edge_performance(self):
        """测试不同规模下add_edge操作的耗时。"""
        for scale in [100, 1000]:
            kg = KnowledgeGraph(save_path=self.save_path)
            # 预先创建节点
            for i in range(scale):
                kg.add_node(f"edge_node_{i}")
            # 测量添加边
            edge_count = min(scale, 500)
            start = time.perf_counter()
            for i in range(edge_count):
                target = (i + 1) % scale
                kg.add_edge(f"edge_node_{i}", f"edge_node_{target}", "关联")
            elapsed = time.perf_counter() - start
            self.assertLess(elapsed, 10.0, f"add_edge {edge_count}条边耗时{elapsed:.3f}s过长")

    # ================================================================
    # save / load 持久化耗时
    # ================================================================

    def test_save_load_performance(self):
        """测试不同规模下save/load持久化的耗时。"""
        for scale in [100, 1000]:
            kg = KnowledgeGraph(save_path=self.save_path)
            self._build_graph(kg, scale, edges_per_node=2)

            # 测量save
            start = time.perf_counter()
            kg.save()
            save_time = time.perf_counter() - start

            # 测量load
            kg2 = KnowledgeGraph(save_path=self.save_path)
            load_start = time.perf_counter()
            kg2.load()
            load_time = time.perf_counter() - load_start

            # 验证数据完整性
            self.assertEqual(len(kg2.nodes), scale)
            self.assertGreater(len(kg2.edges), 0)

            # 持久化应在合理时间内完成
            self.assertLess(save_time, 5.0, f"save {scale}节点耗时{save_time:.3f}s过长")
            self.assertLess(load_time, 5.0, f"load {scale}节点耗时{load_time:.3f}s过长")

    # ================================================================
    # derive_new_tasks 推演耗时
    # ================================================================

    def test_derive_new_tasks_performance(self):
        """测试不同规模下derive_new_tasks推演的耗时。"""
        for scale in [100, 1000]:
            kg = KnowledgeGraph(save_path=self.save_path)
            self._build_graph(kg, scale, edges_per_node=3)

            start = time.perf_counter()
            tasks = kg.derive_new_tasks("node_0", weight_threshold=0.1)
            elapsed = time.perf_counter() - start

            self.assertGreater(len(tasks), 0)
            self.assertLess(elapsed, 5.0, f"derive {scale}节点推演耗时{elapsed:.3f}s过长")

    # ================================================================
    # get_stats 统计耗时
    # ================================================================

    def test_get_stats_performance(self):
        """测试不同规模下get_stats统计的耗时。"""
        for scale in [100, 1000, 10000]:
            kg = KnowledgeGraph(save_path=self.save_path)
            self._build_graph(kg, scale, edges_per_node=2)

            start = time.perf_counter()
            stats = kg.get_stats()
            elapsed = time.perf_counter() - start

            self.assertEqual(stats["total_nodes"], scale)
            self.assertLess(elapsed, 5.0, f"get_stats {scale}节点耗时{elapsed:.3f}s过长")

    # ================================================================
    # 基准报告输出
    # ================================================================

    def test_performance_report(self):
        """生成完整的性能基准报告。"""
        report_lines = ["=" * 60]
        report_lines.append("  永动知识图谱 Agent - 性能基准报告")
        report_lines.append("=" * 60)

        for scale in [100, 1000]:
            kg = KnowledgeGraph(save_path=self.save_path)
            self._build_graph(kg, scale, edges_per_node=2)

            # add_node
            start = time.perf_counter()
            for i in range(scale):
                kg.add_node(f"bench_node_{i}")
            add_node_time = time.perf_counter() - start

            # add_edge
            edge_count = scale * 2
            start = time.perf_counter()
            for i in range(scale):
                kg.add_edge(f"bench_node_{i}", f"bench_node_{(i+1)%scale}", "r1")
            add_edge_time = time.perf_counter() - start

            # save
            start = time.perf_counter()
            kg.save()
            save_time = time.perf_counter() - start

            # load
            kg2 = KnowledgeGraph(save_path=self.save_path)
            start = time.perf_counter()
            kg2.load()
            load_time = time.perf_counter() - start

            # derive
            start = time.perf_counter()
            tasks = kg.derive_new_tasks("bench_node_0", weight_threshold=0.1)
            derive_time = time.perf_counter() - start

            # stats
            start = time.perf_counter()
            kg.get_stats()
            stats_time = time.perf_counter() - start

            report_lines.append(f"\n  规模: {scale} 节点 / {len(kg.edges)} 边")
            report_lines.append(f"    add_node  ({scale}次): {add_node_time*1000:.2f}ms")
            report_lines.append(f"    add_edge  ({scale}次): {add_edge_time*1000:.2f}ms")
            report_lines.append(f"    save:              {save_time*1000:.2f}ms")
            report_lines.append(f"    load:              {load_time*1000:.2f}ms")
            report_lines.append(f"    derive_new_tasks:  {derive_time*1000:.2f}ms ({len(tasks)}个任务)")
            report_lines.append(f"    get_stats:          {stats_time*1000:.2f}ms")

        report_lines.append("\n" + "=" * 60)
        report_str = "\n".join(report_lines)

        # 输出报告到stdout
        print(f"\n{report_str}")

        # 基本断言：报告已生成
        self.assertIn("性能基准报告", report_str)
        self.assertIn("100 节点", report_str)
        self.assertIn("1000 节点", report_str)


if __name__ == "__main__":
    unittest.main()
