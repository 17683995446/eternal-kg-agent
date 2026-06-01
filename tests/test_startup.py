# -*- coding: utf-8 -*-
"""
永动知识图谱 Agent - 启动流程测试
阶段91: 测试启动自检、种子注入、实例锁、优雅关闭
公理溯源: 存续公理 - 测试是验证系统启动可靠性的手段
设计原则: 使用unittest + tempfile，测试隔离无副作用
"""

import json
import os
import tempfile
import shutil
import unittest

from src.agent.instance_lock import InstanceLock
from src.agent.startup import StartupManager
from src.kg.knowledge_graph import KnowledgeGraph
from src.path_manager import PathManager
from src.task.task import Task
from src.task.task_queue import TaskQueue


class TestInstanceLock(unittest.TestCase):
    """测试实例锁的多实例冲突检测。"""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.lock_path = os.path.join(self.tmp_dir, ".test.lock")

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_acquire_and_release(self):
        """获取锁后应可正常释放。"""
        lock = InstanceLock(self.lock_path)
        self.assertTrue(lock.acquire())
        self.assertTrue(lock.is_locked)
        lock.release()
        self.assertFalse(lock.is_locked)

    def test_context_manager(self):
        """上下文管理器应自动获取和释放锁。"""
        lock = InstanceLock(self.lock_path)
        with lock:
            self.assertTrue(lock.is_locked)
        self.assertFalse(lock.is_locked)

    def test_double_acquire_fails(self):
        """同一进程内二次获取应失败（非阻塞模式）。"""
        lock1 = InstanceLock(self.lock_path)
        lock2 = InstanceLock(self.lock_path)
        self.assertTrue(lock1.acquire())
        self.assertFalse(lock2.acquire())
        lock1.release()

    def test_release_without_acquire(self):
        """未获取锁时释放不应报错。"""
        lock = InstanceLock(self.lock_path)
        lock.release()  # 不应抛异常
        self.assertFalse(lock.is_locked)


class TestStartupManagerPreLaunch(unittest.TestCase):
    """测试启动自检。"""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.pm = PathManager(self.tmp_dir)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_pre_launch_check_passes(self):
        """正常目录应通过自检。"""
        startup = StartupManager(self.pm)
        self.assertTrue(startup.pre_launch_check())

    def test_pre_launch_check_creates_data_dir(self):
        """自检应自动创建数据目录。"""
        data_dir = os.path.join(self.tmp_dir, "data")
        startup = StartupManager(PathManager(self.tmp_dir))
        startup.pre_launch_check()
        self.assertTrue(os.path.exists(data_dir))

    def test_pre_launch_check_readonly_dir_fails(self):
        """只读目录应导致自检失败。"""
        # 创建只读目录
        readonly_dir = os.path.join(self.tmp_dir, "readonly")
        os.makedirs(readonly_dir, exist_ok=True)
        os.chmod(readonly_dir, 0o444)

        pm = PathManager(readonly_dir)
        startup = StartupManager(pm)
        # 写入测试文件应失败
        result = startup.pre_launch_check()

        # 恢复权限以便清理
        os.chmod(readonly_dir, 0o755)

        # 在某些环境下root用户不受权限限制，所以只检查是否有错误记录
        if os.getuid() == 0:
            # root用户可以写入只读目录，跳过此断言
            pass
        else:
            self.assertFalse(result)


class TestStartupManagerSeedKnowledge(unittest.TestCase):
    """测试种子知识注入。"""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        kg_path = os.path.join(self.tmp_dir, "test_kg.json")
        self.kg = KnowledgeGraph(save_path=kg_path)
        self.pm = PathManager(self.tmp_dir)
        self.startup = StartupManager(self.pm)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_inject_seed_knowledge(self):
        """冷启动时应注入种子节点。"""
        count = self.startup.inject_seed_knowledge(self.kg)
        self.assertGreater(count, 0)
        # 验证关键节点存在
        self.assertIsNotNone(self.kg.get_node_by_name("系统自身"))
        self.assertIsNotNone(self.kg.get_node_by_name("存续公理"))
        self.assertIsNotNone(self.kg.get_node_by_name("记忆公理"))
        self.assertIsNotNone(self.kg.get_node_by_name("自驱公理"))

    def test_inject_seed_knowledge_idempotent(self):
        """重复注入不应创建重复节点。"""
        count1 = self.startup.inject_seed_knowledge(self.kg)
        count2 = self.startup.inject_seed_knowledge(self.kg)
        self.assertGreater(count1, 0)
        self.assertEqual(count2, 0)

    def test_seed_edges_created(self):
        """种子边应被正确创建。"""
        self.startup.inject_seed_knowledge(self.kg)
        stats = self.kg.get_stats()
        self.assertGreater(stats["total_edges"], 0)


class TestStartupManagerGracefulShutdown(unittest.TestCase):
    """测试优雅关闭。"""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        kg_path = os.path.join(self.tmp_dir, "test_kg.json")
        tq_path = os.path.join(self.tmp_dir, "test_tq.json")
        self.kg = KnowledgeGraph(save_path=kg_path)
        self.task_queue = TaskQueue()
        self.pm = PathManager(self.tmp_dir)
        self.startup = StartupManager(self.pm)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_graceful_shutdown_saves_kg(self):
        """优雅关闭应保存知识图谱。"""
        self.kg.add_node("测试节点")
        self.startup.graceful_shutdown(self.kg, self.task_queue)
        self.assertTrue(os.path.exists(self.kg.save_path))

    def test_graceful_shutdown_releases_lock(self):
        """优雅关闭应释放实例锁。"""
        self.startup.instance_lock.acquire()
        self.startup.graceful_shutdown(self.kg, self.task_queue)
        self.assertFalse(self.startup.instance_lock.is_locked)


class TestAgentInitAndTask(unittest.TestCase):
    """测试Agent初始化与初始任务注入。"""

    def test_agent_initialization(self):
        """Agent应正确初始化所有子系统。"""
        from src.agent.agent import EternalSelfAgent
        agent = EternalSelfAgent()
        self.assertIsNotNone(agent.path_manager)
        self.assertIsNotNone(agent.clock)
        self.assertIsNotNone(agent.knowledge_graph)
        self.assertIsNotNone(agent.task_queue)
        self.assertIsNotNone(agent._eternal_loop)
        self.assertIsNotNone(agent.startup_manager)

    def test_inject_initial_task(self):
        """初始任务应成功注入。"""
        from src.agent.agent import EternalSelfAgent
        agent = EternalSelfAgent()
        result = agent.inject_initial_task()
        self.assertTrue(result)
        self.assertEqual(agent.task_queue.size, 1)
        task = agent.task_queue.peek()
        self.assertEqual(task.name, "系统初始认知迭代")

    def test_inject_initial_task_idempotent(self):
        """重复注入初始任务应被去重拒绝。"""
        from src.agent.agent import EternalSelfAgent
        agent = EternalSelfAgent()
        agent.inject_initial_task()
        result = agent.inject_initial_task()
        self.assertFalse(result)
        self.assertEqual(agent.task_queue.size, 1)


if __name__ == "__main__":
    unittest.main()
