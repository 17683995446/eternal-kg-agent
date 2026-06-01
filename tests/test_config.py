# -*- coding: utf-8 -*-
"""
永动知识图谱 Agent - 配置常量单元测试
公理溯源: 存续公理 - 测试是验证系统参数正确性的手段
设计原则: 使用标准unittest，零外部依赖
"""

import os
import sys
import unittest

# 确保项目根目录在搜索路径中
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import (
    EVOLVE_STEP,
    KG_SAVE_PATH,
    LOOP_DELAY,
    LOG_FILE_PATH,
    SYSTEM_VERSION,
    TASK_QUEUE_MAX,
    TASK_QUEUE_SAVE_PATH,
)


class TestConfig(unittest.TestCase):
    """验证config.py中所有常量的类型和值"""

    def test_loop_delay_type_and_value(self):
        """LOOP_DELAY应为float类型，值为0.3"""
        self.assertIsInstance(LOOP_DELAY, float)
        self.assertEqual(LOOP_DELAY, 0.3)

    def test_evolve_step_type_and_value(self):
        """EVOLVE_STEP应为int类型，值为50"""
        self.assertIsInstance(EVOLVE_STEP, int)
        self.assertEqual(EVOLVE_STEP, 50)

    def test_kg_save_path_type_and_value(self):
        """KG_SAVE_PATH应为str类型，值为data/knowledge_graph.json"""
        self.assertIsInstance(KG_SAVE_PATH, str)
        self.assertEqual(KG_SAVE_PATH, "data/knowledge_graph.json")

    def test_task_queue_save_path_type_and_value(self):
        """TASK_QUEUE_SAVE_PATH应为str类型，值为data/task_queue.json"""
        self.assertIsInstance(TASK_QUEUE_SAVE_PATH, str)
        self.assertEqual(TASK_QUEUE_SAVE_PATH, "data/task_queue.json")

    def test_log_file_path_type_and_value(self):
        """LOG_FILE_PATH应为str类型，值为data/system.log"""
        self.assertIsInstance(LOG_FILE_PATH, str)
        self.assertEqual(LOG_FILE_PATH, "data/system.log")

    def test_task_queue_max_type_and_value(self):
        """TASK_QUEUE_MAX应为int类型，值为200"""
        self.assertIsInstance(TASK_QUEUE_MAX, int)
        self.assertEqual(TASK_QUEUE_MAX, 200)

    def test_system_version_type_and_value(self):
        """SYSTEM_VERSION应为str类型，值为1.0.0"""
        self.assertIsInstance(SYSTEM_VERSION, str)
        self.assertEqual(SYSTEM_VERSION, "1.0.0")


if __name__ == "__main__":
    unittest.main()
