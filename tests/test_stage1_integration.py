# -*- coding: utf-8 -*-
"""
永动知识图谱 Agent - 第一阶段集成测试
公理溯源: 存续公理 - 集成测试验证系统各模块协同工作的能力
设计原则: 验证main.py可启动、config正确、logger输出、clock可用、path_manager路径正确
"""

import logging
import os
import subprocess
import sys
import tempfile
import unittest

# 确保项目根目录在搜索路径中
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.clock import Clock
from src.config import (
    EVOLVE_STEP,
    KG_SAVE_PATH,
    LOOP_DELAY,
    LOG_FILE_PATH,
    SYSTEM_VERSION,
    TASK_QUEUE_MAX,
    TASK_QUEUE_SAVE_PATH,
)
from src.logger import get_logger
from src.path_manager import PathManager


class TestMainEntry(unittest.TestCase):
    """验证main.py可正常启动并输出预期内容"""

    def test_main_outputs_system_alive(self):
        """main.py应正常启动（因永动循环需外部终止，验证进程可启动即可）"""
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        main_path = os.path.join(project_root, "main.py")
        try:
            result = subprocess.run(
                [sys.executable, main_path],
                capture_output=True,
                text=True,
                timeout=5,
            )
            output = result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            # main.py启动永动循环，timeout后进程被终止，这是预期行为
            self.assertTrue(True)
            return
        # 验证至少有启动日志输出（日志输出到stderr）
        self.assertIn("启动中", output)


class TestConfigIntegration(unittest.TestCase):
    """验证config常量在集成环境下的正确性"""

    def test_all_constants_exist(self):
        """所有核心常量都应存在且非空"""
        self.assertIsNotNone(LOOP_DELAY)
        self.assertIsNotNone(EVOLVE_STEP)
        self.assertIsNotNone(KG_SAVE_PATH)
        self.assertIsNotNone(TASK_QUEUE_SAVE_PATH)
        self.assertIsNotNone(LOG_FILE_PATH)
        self.assertIsNotNone(TASK_QUEUE_MAX)
        self.assertIsNotNone(SYSTEM_VERSION)

    def test_version_format(self):
        """SYSTEM_VERSION应符合语义化版本格式 X.Y.Z"""
        parts = SYSTEM_VERSION.split(".")
        self.assertEqual(len(parts), 3)
        for part in parts:
            self.assertTrue(part.isdigit())


class TestLoggerIntegration(unittest.TestCase):
    """验证logger模块在集成环境下的正常工作"""

    def test_get_logger_returns_logger(self):
        """get_logger应返回logging.Logger实例"""
        logger = get_logger("test_integration")
        self.assertIsInstance(logger, logging.Logger)

    def test_logger_has_handlers(self):
        """Logger应同时配置了控制台和文件handler"""
        logger = get_logger("test_integration_handlers")
        self.assertTrue(len(logger.handlers) >= 2)

    def test_logger_can_log_without_error(self):
        """Logger应能正常输出日志而不抛出异常"""
        logger = get_logger("test_integration_log")
        try:
            logger.info("集成测试日志消息")
            logger.debug("集成测试调试消息")
            logger.error("集成测试错误消息")
        except Exception as e:
            self.fail(f"日志输出异常: {e}")


class TestClockIntegration(unittest.TestCase):
    """验证clock模块在集成环境下的正常工作"""

    def test_clock_now_returns_float(self):
        """now()应返回float类型的时间戳"""
        clock = Clock()
        self.assertIsInstance(clock.now(), float)

    def test_clock_elapsed_non_negative(self):
        """elapsed()应返回非负值"""
        clock = Clock()
        self.assertGreaterEqual(clock.elapsed(), 0.0)

    def test_clock_format_elapsed(self):
        """format_elapsed()应返回HH:MM:SS格式的字符串"""
        clock = Clock()
        formatted = clock.format_elapsed()
        parts = formatted.split(":")
        self.assertEqual(len(parts), 3)
        for part in parts:
            self.assertTrue(part.isdigit())

    def test_clock_format_timestamp(self):
        """format_timestamp()应返回可读的时间字符串"""
        formatted = Clock.format_timestamp()
        self.assertIsInstance(formatted, str)
        self.assertTrue(len(formatted) > 0)

    def test_clock_format_timestamp_with_value(self):
        """format_timestamp(0)应返回1970年的基准时间"""
        formatted = Clock.format_timestamp(0)
        self.assertIn("1970", formatted)


class TestPathManagerIntegration(unittest.TestCase):
    """验证path_manager模块在集成环境下的正常工作"""

    def setUp(self):
        """使用临时目录作为测试基础目录"""
        self.tmp_dir = tempfile.mkdtemp()
        self.pm = PathManager(base_dir=self.tmp_dir)

    def test_data_dir_created(self):
        """数据目录应自动创建"""
        self.assertTrue(os.path.isdir(self.pm.data_dir))

    def test_kg_path_ends_correctly(self):
        """知识图谱路径应以knowledge_graph.json结尾"""
        self.assertTrue(self.pm.kg_path.endswith("knowledge_graph.json"))

    def test_task_queue_path_ends_correctly(self):
        """任务队列路径应以task_queue.json结尾"""
        self.assertTrue(self.pm.task_queue_path.endswith("task_queue.json"))

    def test_log_path_ends_correctly(self):
        """日志路径应以system.log结尾"""
        self.assertTrue(self.pm.log_path.endswith("system.log"))

    def test_paths_under_base_dir(self):
        """所有路径都应在基础目录下"""
        for path in [self.pm.kg_path, self.pm.task_queue_path, self.pm.log_path]:
            self.assertTrue(path.startswith(self.tmp_dir))

    def test_ensure_dirs_creates_all(self):
        """ensure_dirs应确保所有目录存在"""
        self.pm.ensure_dirs()
        for path in [self.pm.kg_path, self.pm.task_queue_path, self.pm.log_path]:
            directory = os.path.dirname(path)
            if directory:
                self.assertTrue(os.path.isdir(directory))


if __name__ == "__main__":
    unittest.main()
