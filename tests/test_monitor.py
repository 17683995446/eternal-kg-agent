# -*- coding: utf-8 -*-
"""
永动知识图谱 Agent - 监控模块测试
阶段92-95: 测试指标采集、快照、执行历史、健康度、报告生成
公理溯源: 存续公理 - 测试是验证监控可靠性的手段
设计原则: 使用unittest + tempfile，测试隔离无副作用
"""

import json
import os
import tempfile
import shutil
import unittest
from unittest.mock import patch, MagicMock

from src.monitor.metrics import MetricsCollector
from src.monitor.snapshot import SystemSnapshot
from src.monitor.execution_history import ExecutionHistory
from src.monitor.health_scorer import HealthScorer
from src.monitor.report_generator import ReportGenerator


class TestMetricsCollector(unittest.TestCase):
    """测试指标采集器。"""

    def test_initial_state(self):
        """初始状态所有计数应为零。"""
        mc = MetricsCollector()
        metrics = mc.collect()
        self.assertEqual(metrics["loop_count"], 0)
        self.assertEqual(metrics["task_completed"], 0)
        self.assertEqual(metrics["task_failed"], 0)
        self.assertEqual(metrics["exception_count"], 0)
        self.assertGreaterEqual(metrics["uptime_seconds"], 0)
        self.assertGreaterEqual(metrics["memory_mb"], 0)

    def test_increment_methods(self):
        """递增方法应正确更新计数。"""
        mc = MetricsCollector()
        mc.increment_loop()
        mc.increment_loop()
        mc.increment_task_completed()
        mc.increment_task_failed()
        mc.increment_exception()

        metrics = mc.collect()
        self.assertEqual(metrics["loop_count"], 2)
        self.assertEqual(metrics["task_completed"], 1)
        self.assertEqual(metrics["task_failed"], 1)
        self.assertEqual(metrics["exception_count"], 1)

    def test_collect_with_params(self):
        """collect应包含传入的kg_stats和queue_size。"""
        mc = MetricsCollector()
        kg_stats = {"total_nodes": 10, "total_edges": 5}
        metrics = mc.collect(kg_stats=kg_stats, queue_size=3)
        self.assertEqual(metrics["kg_stats"], kg_stats)
        self.assertEqual(metrics["queue_size"], 3)

    def test_to_dict_same_as_collect(self):
        """to_dict应返回与collect相同的结果。"""
        mc = MetricsCollector()
        self.assertEqual(mc.to_dict(), mc.collect())


class TestSystemSnapshot(unittest.TestCase):
    """测试系统快照。"""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_take_returns_dict(self):
        """take应返回包含时间戳和指标的字典。"""
        ss = SystemSnapshot(save_dir=self.tmp_dir)
        metrics = {"uptime_seconds": 100}
        snapshot = ss.take(metrics, queue_size=5)
        self.assertIn("timestamp", snapshot)
        self.assertIn("formatted_time", snapshot)
        self.assertIn("metrics", snapshot)
        self.assertEqual(snapshot["queue_size"], 5)

    def test_save_creates_file(self):
        """save应创建JSON文件。"""
        ss = SystemSnapshot(save_dir=self.tmp_dir)
        snapshot = ss.take({"uptime_seconds": 100})
        filepath = ss.save(snapshot)
        self.assertTrue(os.path.exists(filepath))

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertIn("timestamp", data)

    def test_save_dir_created(self):
        """快照目录不存在时应自动创建。"""
        new_dir = os.path.join(self.tmp_dir, "new_snapshots")
        ss = SystemSnapshot(save_dir=new_dir)
        self.assertTrue(os.path.exists(new_dir))


class TestExecutionHistory(unittest.TestCase):
    """测试执行历史记录器。"""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.history_path = os.path.join(self.tmp_dir, "history.json")

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_record_and_get_recent(self):
        """记录后应能获取最近记录。"""
        eh = ExecutionHistory(save_path=self.history_path)
        eh.record("任务A", 1.0, 2.0, "success", 1)
        eh.record("任务B", 2.0, 3.0, "success", 0)
        eh.record("任务C", 3.0, 4.0, "failed", 2)

        recent = eh.get_recent(2)
        self.assertEqual(len(recent), 2)
        # 最近记录在前
        self.assertEqual(recent[0]["task_name"], "任务C")
        self.assertEqual(recent[1]["task_name"], "任务B")

    def test_record_duration(self):
        """记录应自动计算耗时。"""
        eh = ExecutionHistory(save_path=self.history_path)
        eh.record("任务X", 1.0, 3.5, "success")
        recent = eh.get_recent(1)
        self.assertAlmostEqual(recent[0]["duration"], 2.5, places=2)

    def test_max_records_limit(self):
        """超过上限时应淘汰最旧记录。"""
        eh = ExecutionHistory(save_path=self.history_path, max_records=5)
        for i in range(10):
            eh.record(f"任务{i}", float(i), float(i + 1), "success")
        self.assertEqual(eh.total_count, 5)
        recent = eh.get_recent(5)
        self.assertEqual(recent[0]["task_name"], "任务9")

    def test_save_and_load(self):
        """持久化后应能正确加载。"""
        eh = ExecutionHistory(save_path=self.history_path)
        eh.record("任务A", 1.0, 2.0, "success", 1)
        eh.record("任务B", 2.0, 3.0, "failed", 0)
        eh.save()

        eh2 = ExecutionHistory(save_path=self.history_path)
        self.assertEqual(eh2.total_count, 2)
        recent = eh2.get_recent(2)
        self.assertEqual(recent[0]["task_name"], "任务B")

    def test_get_stats_empty(self):
        """空历史应返回零值统计。"""
        eh = ExecutionHistory(save_path=self.history_path)
        stats = eh.get_stats()
        self.assertEqual(stats["total"], 0)
        self.assertEqual(stats["avg_duration"], 0.0)

    def test_get_stats_with_data(self):
        """有数据时应返回正确统计。"""
        eh = ExecutionHistory(save_path=self.history_path)
        eh.record("任务A", 1.0, 2.0, "success", 1)
        eh.record("任务B", 2.0, 4.0, "success", 2)
        eh.record("任务C", 3.0, 3.5, "failed", 0)

        stats = eh.get_stats()
        self.assertEqual(stats["total"], 3)
        self.assertAlmostEqual(stats["success_rate"], 2 / 3, places=2)
        self.assertEqual(stats["total_derived"], 3)


class TestHealthScorer(unittest.TestCase):
    """测试健康度评分器。"""

    def test_perfect_health(self):
        """无异常、低内存、高完成率应得高分。"""
        scorer = HealthScorer()
        metrics = {
            "task_completed": 10,
            "task_failed": 0,
            "exception_count": 0,
            "loop_count": 100,
            "memory_mb": 50,
            "kg_stats": {
                "total_nodes": 20,
                "valid_nodes": 20,
                "total_edges": 15,
                "avg_weight": 0.5,
            },
        }
        score = scorer.calculate(metrics)
        self.assertGreaterEqual(score, 80)

    def test_poor_health(self):
        """高异常、高内存、低完成率应得低分。"""
        scorer = HealthScorer()
        metrics = {
            "task_completed": 1,
            "task_failed": 9,
            "exception_count": 50,
            "loop_count": 100,
            "memory_mb": 400,
            "kg_stats": {
                "total_nodes": 10,
                "valid_nodes": 3,
                "total_edges": 1,
                "avg_weight": 0.1,
            },
        }
        score = scorer.calculate(metrics)
        self.assertLess(score, 40)

    def test_score_range(self):
        """评分应始终在0-100范围内。"""
        scorer = HealthScorer()
        for _ in range(10):
            metrics = {
                "task_completed": 0,
                "task_failed": 0,
                "exception_count": 0,
                "loop_count": 0,
                "memory_mb": 0,
                "kg_stats": {},
            }
            score = scorer.calculate(metrics)
            self.assertGreaterEqual(score, 0)
            self.assertLessEqual(score, 100)

    def test_with_history_stats(self):
        """传入历史统计不应报错。"""
        scorer = HealthScorer()
        metrics = {
            "task_completed": 5,
            "task_failed": 1,
            "exception_count": 2,
            "loop_count": 50,
            "memory_mb": 80,
            "kg_stats": {
                "total_nodes": 15,
                "valid_nodes": 14,
                "total_edges": 10,
                "avg_weight": 0.5,
            },
        }
        history_stats = {
            "total": 6,
            "avg_duration": 1.5,
            "success_rate": 0.83,
            "total_derived": 3,
        }
        score = scorer.calculate(metrics, history_stats)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)


class TestReportGenerator(unittest.TestCase):
    """测试报告生成器。"""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_generate_returns_string(self):
        """generate应返回非空字符串。"""
        rg = ReportGenerator()
        report = rg.generate(
            metrics={"uptime_seconds": 100, "loop_count": 50},
            health_score=85.5,
        )
        self.assertIsInstance(report, str)
        self.assertIn("运行报告", report)
        self.assertIn("85.5", report)

    def test_generate_with_all_data(self):
        """完整数据应生成完整报告。"""
        rg = ReportGenerator()
        metrics = {
            "uptime_seconds": 3600,
            "loop_count": 1000,
            "task_completed": 50,
            "task_failed": 2,
            "exception_count": 1,
            "memory_mb": 75.3,
            "queue_size": 5,
            "kg_stats": {
                "total_nodes": 30,
                "valid_nodes": 28,
                "total_edges": 20,
                "avg_weight": 0.55,
            },
        }
        history_stats = {
            "total": 52,
            "avg_duration": 0.5,
            "success_rate": 0.96,
            "total_derived": 10,
        }
        report = rg.generate(metrics, history_stats, 92.0)
        self.assertIn("知识图谱", report)
        self.assertIn("执行历史", report)
        self.assertIn("健康度", report)
        self.assertIn("优秀", report)

    def test_health_label(self):
        """健康标签应正确映射。"""
        self.assertEqual(ReportGenerator._health_label(90), "优秀")
        self.assertEqual(ReportGenerator._health_label(70), "良好")
        self.assertEqual(ReportGenerator._health_label(50), "一般")
        self.assertEqual(ReportGenerator._health_label(30), "较差")
        self.assertEqual(ReportGenerator._health_label(10), "危险")

    def test_save_report(self):
        """save_report应创建文件。"""
        rg = ReportGenerator()
        report = rg.generate({"uptime_seconds": 10}, health_score=50)
        save_path = os.path.join(self.tmp_dir, "test_report.txt")
        result_path = rg.save_report(report, save_path)
        self.assertTrue(os.path.exists(result_path))

        with open(result_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("运行报告", content)


class TestMonitorIntegration(unittest.TestCase):
    """监控模块集成测试。"""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.history_path = os.path.join(self.tmp_dir, "history.json")

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_full_monitoring_pipeline(self):
        """完整监控流水线：采集 -> 记录 -> 评分 -> 报告。"""
        mc = MetricsCollector()
        mc.increment_loop()
        mc.increment_loop()
        mc.increment_task_completed()

        eh = ExecutionHistory(save_path=self.history_path)
        eh.record("测试任务", 1.0, 2.0, "success", 1)

        metrics = mc.collect(
            kg_stats={"total_nodes": 10, "valid_nodes": 10,
                       "total_edges": 5, "avg_weight": 0.5},
            queue_size=3,
        )

        scorer = HealthScorer()
        score = scorer.calculate(metrics, eh.get_stats())

        rg = ReportGenerator()
        report = rg.generate(metrics, eh.get_stats(), score)

        # 验证报告包含关键信息
        self.assertIn("循环次数: 2", report)
        self.assertIn("任务完成: 1", report)
        self.assertGreater(score, 0)
        self.assertLessEqual(score, 100)


if __name__ == "__main__":
    unittest.main()
