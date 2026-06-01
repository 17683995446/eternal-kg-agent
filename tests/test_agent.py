# -*- coding: utf-8 -*-
"""
永动知识图谱 Agent - 智能体核心集成测试
公理溯源:
  - 存续公理: 测试验证智能体初始化、健康检查、自愈等存续能力
  - 记忆公理: 测试验证任务执行后知识沉淀的正确性
  - 自驱公理: 测试验证任务获取、空闲进化、自主衍生等自驱行为
阶段55: 端到端测试 - 初始化->注入任务->执行->知识沉淀->队列空->空闲进化->异常自愈
设计原则: 使用unittest，mock控制循环，使用base_dir参数隔离持久化数据
"""

import os
import sys
import tempfile
import time
import unittest
from unittest.mock import patch, MagicMock

# 确保项目根目录在搜索路径中
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.agent.agent import EternalSelfAgent
from src.task.task import Task


class TestAgentInit(unittest.TestCase):
    """阶段46-47: 测试智能体初始化。"""

    def setUp(self):
        """每个测试使用独立的临时目录。"""
        self.tmp_dir = tempfile.mkdtemp()

    def test_initial_state(self):
        """初始化后所有核心组件应就绪。"""
        agent = EternalSelfAgent(base_dir=self.tmp_dir)
        self.assertIsNotNone(agent.knowledge_graph)
        self.assertIsNotNone(agent.task_queue)
        self.assertIsNotNone(agent.clock)
        self.assertEqual(agent.run_counter, 0)
        self.assertTrue(agent.system_alive)
        self.assertEqual(agent.error_count, 0)

    def test_load_empty_state(self):
        """无持久化文件时应正常初始化为空状态。"""
        agent = EternalSelfAgent(base_dir=self.tmp_dir)
        self.assertEqual(agent.knowledge_graph.get_stats()["total_nodes"], 0)
        self.assertTrue(agent.task_queue.is_empty())


class TestGetCurrentTask(unittest.TestCase):
    """阶段48: 测试获取当前任务。"""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()

    def test_get_task_from_queue(self):
        """队列有任务时应返回Task实例。"""
        agent = EternalSelfAgent(base_dir=self.tmp_dir)
        agent.task_queue.add_task(Task(name="测试任务"))
        task = agent.get_current_task()
        self.assertIsNotNone(task)
        self.assertEqual(task.name, "测试任务")

    def test_get_task_empty_queue(self):
        """队列空时应返回None。"""
        agent = EternalSelfAgent(base_dir=self.tmp_dir)
        task = agent.get_current_task()
        self.assertIsNone(task)


class TestIdleSelfEvolve(unittest.TestCase):
    """阶段49: 测试空闲进化。"""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()

    def test_idle_evolve_logs_stats(self):
        """空闲进化应记录图谱统计信息。"""
        agent = EternalSelfAgent(base_dir=self.tmp_dir)
        agent.knowledge_graph.add_node("测试节点")
        agent.knowledge_graph.add_edge("A", "B", "关联")
        # add_edge会自动创建A和B节点，加上手动添加的"测试节点"，共3个节点

        with patch.object(agent.logger, "info") as mock_info:
            agent.idle_self_evolve()
            mock_info.assert_called_once()
            msg = mock_info.call_args[0][0]
            self.assertIn("空闲进化", msg)
            self.assertIn("3节点", msg)
            self.assertIn("1边", msg)


class TestExecuteTask(unittest.TestCase):
    """阶段50-51: 测试任务执行与知识沉淀联动。"""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()

    def test_task_creates_kg_node(self):
        """执行任务后任务名应作为节点存在于图谱中。"""
        agent = EternalSelfAgent(base_dir=self.tmp_dir)
        task = Task(name="探索任务")
        agent.execute_task(task)
        node = agent.knowledge_graph.get_node_by_name("探索任务")
        self.assertIsNotNone(node)

    def test_task_creates_derivation_edge(self):
        """执行任务后应创建'自主衍生'边指向下一迭代任务。"""
        agent = EternalSelfAgent(base_dir=self.tmp_dir)
        agent.run_counter = 5
        task = Task(name="原始任务")
        agent.execute_task(task)

        # 验证"自主衍生"边存在
        source_node = agent.knowledge_graph.get_node_by_name("原始任务")
        self.assertIsNotNone(source_node)
        edges = agent.knowledge_graph.get_edges_by_source(source_node.id)
        self.assertEqual(len(edges), 1)
        self.assertEqual(edges[0].relation_name, "自主衍生")

    def test_task_creates_next_iteration_task(self):
        """执行任务后应将下一迭代任务入队。"""
        agent = EternalSelfAgent(base_dir=self.tmp_dir)
        agent.run_counter = 10
        task = Task(name="当前任务")
        agent.execute_task(task)

        # 队列中应有衍生任务
        self.assertEqual(agent.task_queue.size, 1)
        next_task = agent.task_queue.get_task()
        self.assertEqual(next_task.name, "系统迭代任务_10")

    def test_task_saves_knowledge_graph(self):
        """执行任务后应保存知识图谱。"""
        agent = EternalSelfAgent(base_dir=self.tmp_dir)
        task = Task(name="保存测试任务")

        with patch.object(agent.knowledge_graph, "save") as mock_save:
            agent.execute_task(task)
            mock_save.assert_called_once()

    def test_derivation_target_node_exists(self):
        """自主衍生的目标节点应存在于图谱中。"""
        agent = EternalSelfAgent(base_dir=self.tmp_dir)
        agent.run_counter = 3
        task = Task(name="源任务")
        agent.execute_task(task)

        target_node = agent.knowledge_graph.get_node_by_name("系统迭代任务_3")
        self.assertIsNotNone(target_node)


class TestHealthCheckAndSelfRepair(unittest.TestCase):
    """阶段52-53: 测试健康检查与自愈。"""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()

    def test_health_check_returns_all_fields(self):
        """健康检查应返回所有核心指标。"""
        agent = EternalSelfAgent(base_dir=self.tmp_dir)
        agent.run_counter = 10
        agent.error_count = 2
        health = agent.health_check()
        self.assertIn("uptime_seconds", health)
        self.assertIn("uptime_formatted", health)
        self.assertIn("run_counter", health)
        self.assertIn("error_count", health)
        self.assertIn("system_alive", health)
        self.assertIn("kg_nodes", health)
        self.assertIn("kg_edges", health)
        self.assertIn("kg_valid_nodes", health)
        self.assertIn("queue_size", health)
        self.assertEqual(health["run_counter"], 10)
        self.assertEqual(health["error_count"], 2)

    def test_health_check_reflects_kg_and_queue(self):
        """健康检查应反映图谱和队列的实际状态。"""
        agent = EternalSelfAgent(base_dir=self.tmp_dir)
        agent.knowledge_graph.add_node("X")
        agent.knowledge_graph.add_edge("X", "Y", "r")
        agent.task_queue.add_task(Task(name="t1"))

        health = agent.health_check()
        self.assertEqual(health["kg_nodes"], 2)
        self.assertEqual(health["kg_edges"], 1)
        self.assertEqual(health["queue_size"], 1)

    def test_self_repair_increments_error_count(self):
        """自愈应递增error_count。"""
        agent = EternalSelfAgent(base_dir=self.tmp_dir)
        agent.self_repair()
        self.assertEqual(agent.error_count, 1)

    def test_self_repair_resets_system_alive(self):
        """自愈应将system_alive重置为True。"""
        agent = EternalSelfAgent(base_dir=self.tmp_dir)
        agent.system_alive = False
        agent.self_repair()
        self.assertTrue(agent.system_alive)


class TestEternalLoop(unittest.TestCase):
    """阶段54: 测试永动循环。"""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()

    def test_loop_stops_when_system_alive_false(self):
        """system_alive=False时循环应停止。"""
        agent = EternalSelfAgent(base_dir=self.tmp_dir)
        agent.system_alive = False

        with patch("src.agent.agent.time.sleep"):
            agent.eternal_loop()

        self.assertEqual(agent.run_counter, 0)

    def test_loop_executes_tasks(self):
        """循环应执行队列中的任务。"""
        agent = EternalSelfAgent(base_dir=self.tmp_dir)
        agent.task_queue.add_task(Task(name="任务A"))
        agent.task_queue.add_task(Task(name="任务B"))

        call_count = [0]

        def controlled_sleep(duration):
            call_count[0] += 1
            if call_count[0] >= 5:
                agent.system_alive = False

        with patch("src.agent.agent.time.sleep", side_effect=controlled_sleep):
            agent.eternal_loop()

        # 至少执行了2个任务（每个任务执行后还会衍生新任务入队）
        self.assertGreaterEqual(agent.run_counter, 2)

    def test_loop_idle_when_no_tasks(self):
        """无任务时循环应进入空闲进化。"""
        agent = EternalSelfAgent(base_dir=self.tmp_dir)
        # 队列为空

        call_count = [0]

        def controlled_sleep(duration):
            call_count[0] += 1
            if call_count[0] >= 3:
                agent.system_alive = False

        with patch("src.agent.agent.time.sleep", side_effect=controlled_sleep):
            with patch.object(agent, "idle_self_evolve") as mock_evolve:
                agent.eternal_loop()
                # 空闲进化应被调用
                mock_evolve.assert_called()

    def test_loop_self_repair_on_exception(self):
        """循环异常时应触发自愈。"""
        agent = EternalSelfAgent(base_dir=self.tmp_dir)
        agent.task_queue.add_task(Task(name="异常任务"))

        call_count = [0]
        original_sleep = time.sleep

        def inject_exception_and_stop(duration):
            call_count[0] += 1
            if call_count[0] >= 4:
                agent.system_alive = False
            original_sleep(0.01)

        # mock execute_task在第二次调用时抛异常
        original_execute = agent.execute_task
        exec_count = [0]

        def failing_execute(task):
            exec_count[0] += 1
            if exec_count[0] >= 2:
                raise RuntimeError("模拟执行异常")
            original_execute(task)

        with patch("src.agent.agent.time.sleep", side_effect=inject_exception_and_stop):
            with patch.object(agent, "execute_task", side_effect=failing_execute):
                agent.eternal_loop()

        # 自愈应被触发，error_count递增
        self.assertGreaterEqual(agent.error_count, 1)
        # 循环因controlled_sleep设置system_alive=False而正常停止
        self.assertFalse(agent.system_alive)

    def test_evolve_step_triggers_knowledge_hint(self):
        """每EVOLVE_STEP步应触发知识精简提示。"""
        agent = EternalSelfAgent(base_dir=self.tmp_dir)
        # 注入足够多的任务
        for i in range(55):
            agent.task_queue.add_task(Task(name=f"批量任务_{i}"))

        def controlled_sleep(duration):
            if agent.run_counter >= 55:
                agent.system_alive = False

        with patch("src.agent.agent.time.sleep", side_effect=controlled_sleep):
            with patch.object(agent.logger, "info") as mock_info:
                agent.eternal_loop()

        # 检查是否有知识精简提示
        evolve_msgs = [
            call for call in mock_info.call_args_list
            if "知识精简提示" in str(call)
        ]
        self.assertGreater(len(evolve_msgs), 0)


class TestAgentEndToEnd(unittest.TestCase):
    """阶段55: 端到端集成测试 - 初始化->注入任务->执行->知识沉淀->队列空->空闲进化->异常自愈。"""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()

    def test_full_lifecycle(self):
        """
        完整生命周期测试：
        1. 初始化智能体
        2. 注入2个任务
        3. 启动循环，执行任务并沉淀知识
        4. 任务执行完后队列空，进入空闲进化
        5. 停止循环
        6. 验证知识图谱中有正确的节点和边
        """
        agent = EternalSelfAgent(base_dir=self.tmp_dir)

        # 注入任务
        agent.task_queue.add_task(Task(name="初始任务_1"))
        agent.task_queue.add_task(Task(name="初始任务_2"))

        # 控制循环：执行完初始任务及其衍生任务后停止
        sleep_count = [0]

        def controlled_sleep(duration):
            sleep_count[0] += 1
            # 限制循环次数防止无限衍生
            if sleep_count[0] >= 10:
                agent.system_alive = False

        with patch("src.agent.agent.time.sleep", side_effect=controlled_sleep):
            agent.eternal_loop()

        # 验证：至少执行了初始任务
        self.assertGreaterEqual(agent.run_counter, 2)

        # 验证：知识图谱中有初始任务节点
        node1 = agent.knowledge_graph.get_node_by_name("初始任务_1")
        node2 = agent.knowledge_graph.get_node_by_name("初始任务_2")
        self.assertIsNotNone(node1)
        self.assertIsNotNone(node2)

        # 验证：有"自主衍生"边
        edges = agent.knowledge_graph.get_edges_by_relation("自主衍生")
        self.assertGreater(len(edges), 0)

    def test_exception_recovery_lifecycle(self):
        """
        异常恢复生命周期测试：
        1. 初始化智能体
        2. 注入任务
        3. 第一次执行正常，第二次执行抛异常
        4. 自愈后继续运行
        5. 停止循环
        6. 验证error_count > 0
        """
        agent = EternalSelfAgent(base_dir=self.tmp_dir)
        agent.task_queue.add_task(Task(name="正常任务"))
        agent.task_queue.add_task(Task(name="异常任务"))

        exec_count = [0]
        original_execute = agent.execute_task

        def failing_execute(task):
            exec_count[0] += 1
            if exec_count[0] == 2:
                raise RuntimeError("模拟异常")
            original_execute(task)

        sleep_count = [0]

        def controlled_sleep(duration):
            sleep_count[0] += 1
            if sleep_count[0] >= 8:
                agent.system_alive = False

        with patch("src.agent.agent.time.sleep", side_effect=controlled_sleep):
            with patch.object(agent, "execute_task", side_effect=failing_execute):
                agent.eternal_loop()

        # 验证异常被捕获并自愈
        self.assertGreaterEqual(agent.error_count, 1)
        self.assertGreaterEqual(agent.run_counter, 1)

    def test_persistence_after_execution(self):
        """
        持久化验证测试：
        1. 创建智能体，执行任务
        2. 销毁智能体
        3. 重新创建智能体，验证知识图谱从文件恢复
        """
        # 第一次启动
        agent1 = EternalSelfAgent(base_dir=self.tmp_dir)
        agent1.task_queue.add_task(Task(name="持久化任务"))
        agent1.run_counter = 1
        agent1.execute_task(Task(name="持久化任务"))

        # 验证图谱已保存
        kg_stats = agent1.knowledge_graph.get_stats()
        self.assertGreater(kg_stats["total_nodes"], 0)

        # 销毁并重建（使用相同base_dir以加载同一持久化文件）
        del agent1
        agent2 = EternalSelfAgent(base_dir=self.tmp_dir)

        # 验证知识图谱恢复
        node = agent2.knowledge_graph.get_node_by_name("持久化任务")
        self.assertIsNotNone(node)
        # 验证衍生任务节点也恢复了
        derived_node = agent2.knowledge_graph.get_node_by_name("系统迭代任务_1")
        self.assertIsNotNone(derived_node)


if __name__ == "__main__":
    unittest.main()
