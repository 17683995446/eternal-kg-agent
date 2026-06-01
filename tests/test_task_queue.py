# -*- coding: utf-8 -*-
"""
永动知识图谱 Agent - 任务队列模块集成测试
阶段35: 覆盖入队→出队→满队→空队→去重→持久化→恢复全流程
公理溯源: 自驱公理 - 测试是系统自我校验的手段
设计原则: 使用unittest，每个测试方法聚焦单一职责，使用临时文件避免污染
"""

import json
import os
import sys
import tempfile
import unittest

# 确保项目根目录在搜索路径中
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.task.task import Task
from src.task.task_queue import TaskQueue


class TestTask(unittest.TestCase):
    """阶段26: Task 数据结构测试。"""

    def test_default_fields(self):
        """默认字段应正确初始化。"""
        t = Task(name="test")
        self.assertEqual(t.name, "test")
        self.assertEqual(t.description, "")
        self.assertEqual(t.priority, 0)
        self.assertEqual(t.status, "pending")
        self.assertEqual(t.result, "")
        self.assertTrue(len(t.id) > 0)
        self.assertTrue(t.created_at > 0)

    def test_custom_fields(self):
        """自定义字段应正确赋值。"""
        t = Task(
            name="custom",
            description="desc",
            priority=5,
            task_id="abc123",
            created_at=1000.0,
            status="running",
            result="ok",
        )
        self.assertEqual(t.id, "abc123")
        self.assertEqual(t.name, "custom")
        self.assertEqual(t.priority, 5)
        self.assertEqual(t.status, "running")
        self.assertEqual(t.result, "ok")

    def test_to_dict_roundtrip(self):
        """序列化→反序列化应保持数据一致。"""
        t = Task(name="roundtrip", description="test", priority=3)
        data = t.to_dict()
        restored = Task.from_dict(data)
        self.assertEqual(restored.id, t.id)
        self.assertEqual(restored.name, t.name)
        self.assertEqual(restored.description, t.description)
        self.assertEqual(restored.priority, t.priority)
        self.assertEqual(restored.status, t.status)
        self.assertEqual(restored.result, t.result)
        self.assertEqual(restored.created_at, t.created_at)

    def test_from_dict_missing_optional_keys(self):
        """反序列化时缺少可选字段应使用默认值。"""
        data = {"id": "x", "name": "minimal"}
        t = Task.from_dict(data)
        self.assertEqual(t.id, "x")
        self.assertEqual(t.name, "minimal")
        self.assertEqual(t.description, "")
        self.assertEqual(t.priority, 0)
        self.assertEqual(t.status, "pending")
        self.assertEqual(t.result, "")


class TestTaskQueue(unittest.TestCase):
    """阶段27-34: TaskQueue 集成测试。"""

    def setUp(self):
        """每个测试使用独立的临时文件和队列。"""
        self.tmp_dir = tempfile.mkdtemp()
        self.save_path = os.path.join(self.tmp_dir, "task_queue.json")
        # 临时替换配置中的保存路径
        self._orig_save_path = os.environ.get("TASK_QUEUE_SAVE_PATH")
        # 直接在TaskQueue中注入路径
        self._patch_save_path(self.save_path)
        self.queue = TaskQueue(max_size=3)

    def _patch_save_path(self, path: str):
        """ monkey-patch TASK_QUEUE_SAVE_PATH 以使用临时文件。"""
        import src.task.task_queue as tq_module
        import src.config as cfg_module

        self._orig_cfg_path = cfg_module.TASK_QUEUE_SAVE_PATH
        cfg_module.TASK_QUEUE_SAVE_PATH = path
        tq_module.TASK_QUEUE_SAVE_PATH = path

    def tearDown(self):
        """恢复原始配置。"""
        import src.task.task_queue as tq_module
        import src.config as cfg_module

        cfg_module.TASK_QUEUE_SAVE_PATH = self._orig_cfg_path
        tq_module.TASK_QUEUE_SAVE_PATH = self._orig_cfg_path

    # ---- 入队/出队 ----

    def test_add_and_get(self):
        """入队后出队应保持FIFO顺序。"""
        t1 = Task(name="a")
        t2 = Task(name="b")
        self.assertTrue(self.queue.add_task(t1))
        self.assertTrue(self.queue.add_task(t2))
        got = self.queue.get_task()
        self.assertEqual(got.name, "a")
        got = self.queue.get_task()
        self.assertEqual(got.name, "b")

    def test_get_from_empty(self):
        """空队列出队应返回None。"""
        self.assertIsNone(self.queue.get_task())

    def test_is_empty(self):
        """空队列应返回True。"""
        self.assertTrue(self.queue.is_empty())
        self.queue.add_task(Task(name="x"))
        self.assertFalse(self.queue.is_empty())

    def test_peek_without_pop(self):
        """peek不应移除队首元素。"""
        self.queue.add_task(Task(name="peek_test"))
        task = self.queue.peek()
        self.assertEqual(task.name, "peek_test")
        self.assertEqual(self.queue.size, 1)

    def test_peek_empty(self):
        """空队列peek应返回None。"""
        self.assertIsNone(self.queue.peek())

    # ---- 满队 ----

    def test_full_queue_rejects(self):
        """队列满后入队应返回False。"""
        for i in range(3):
            self.assertTrue(self.queue.add_task(Task(name=f"t{i}")))
        self.assertTrue(self.queue.is_full())
        self.assertFalse(self.queue.add_task(Task(name="overflow")))

    def test_size_property(self):
        """size应准确反映队列长度。"""
        self.assertEqual(self.queue.size, 0)
        self.queue.add_task(Task(name="a"))
        self.assertEqual(self.queue.size, 1)
        self.queue.add_task(Task(name="b"))
        self.assertEqual(self.queue.size, 2)

    # ---- 去重 ----

    def test_duplicate_name_rejected(self):
        """重名任务应被拒绝。"""
        self.assertTrue(self.queue.add_task(Task(name="dup")))
        self.assertFalse(self.queue.add_task(Task(name="dup")))

    def test_duplicate_after_pop(self):
        """出队后同名任务应可重新入队。"""
        self.queue.add_task(Task(name="reuse"))
        self.queue.get_task()
        self.assertTrue(self.queue.add_task(Task(name="reuse")))

    # ---- 批量入队 ----

    def test_batch_add(self):
        """批量入队应返回实际入队数。"""
        tasks = [Task(name=f"batch_{i}") for i in range(5)]
        count = self.queue.batch_add_tasks(tasks)
        self.assertEqual(count, 3)  # max_size=3
        self.assertEqual(self.queue.size, 3)

    def test_batch_add_skips_duplicates(self):
        """批量入队应跳过重复名称。"""
        self.queue.add_task(Task(name="exist"))
        tasks = [
            Task(name="exist"),    # 重复
            Task(name="new1"),    # 新
            Task(name="new2"),    # 新
        ]
        count = self.queue.batch_add_tasks(tasks)
        self.assertEqual(count, 2)
        self.assertEqual(self.queue.size, 3)

    # ---- 持久化与恢复 ----

    def test_save_and_load(self):
        """保存后新建队列应能恢复数据。"""
        self.queue.add_task(Task(name="persist_a", priority=1))
        self.queue.add_task(Task(name="persist_b", priority=2))
        self.queue.save()

        # 用新队列实例从文件恢复
        restored = TaskQueue(max_size=3)
        self.assertEqual(restored.size, 2)
        t = restored.get_task()
        self.assertEqual(t.name, "persist_a")
        self.assertEqual(t.priority, 1)
        t = restored.get_task()
        self.assertEqual(t.name, "persist_b")
        self.assertEqual(t.priority, 2)

    def test_save_creates_file(self):
        """save应创建JSON文件。"""
        self.queue.add_task(Task(name="file_test"))
        self.queue.save()
        self.assertTrue(os.path.isfile(self.save_path))

        with open(self.save_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "file_test")

    def test_load_from_nonexistent_file(self):
        """文件不存在时load应静默使用空队列。"""
        os.remove(self.save_path) if os.path.exists(self.save_path) else None
        q = TaskQueue(max_size=3)
        self.assertTrue(q.is_empty())

    def test_load_from_corrupt_file(self):
        """损坏的JSON文件不应导致崩溃，应使用空队列。"""
        with open(self.save_path, "w", encoding="utf-8") as f:
            f.write("{invalid json!!!")
        q = TaskQueue(max_size=3)
        self.assertTrue(q.is_empty())

    # ---- 清空 ----

    def test_clear(self):
        """clear应清空队列和去重集合。"""
        self.queue.add_task(Task(name="c1"))
        self.queue.add_task(Task(name="c2"))
        self.queue.clear()
        self.assertTrue(self.queue.is_empty())
        self.assertEqual(self.queue.size, 0)
        # 清空后应可重新入队同名任务
        self.assertTrue(self.queue.add_task(Task(name="c1")))

    # ---- FIFO顺序完整性 ----

    def test_fifo_order_integrity(self):
        """多轮入队出队应严格保持FIFO。"""
        names = ["first", "second", "third"]
        for n in names:
            self.queue.add_task(Task(name=n))
        for expected in names:
            got = self.queue.get_task()
            self.assertEqual(got.name, expected)
        self.assertTrue(self.queue.is_empty())


if __name__ == "__main__":
    unittest.main()
