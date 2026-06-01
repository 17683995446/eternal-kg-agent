# -*- coding: utf-8 -*-
"""
永动知识图谱 Agent - 永续循环引擎集成测试
公理溯源: 存续公理 - 测试是验证系统存续能力的手段
阶段45: 正常循环 / 异常注入 / 自愈恢复 / 信号退出
设计原则: 使用unittest，循环可控（短延时+计数限制）
"""

import signal
import time
import unittest
from unittest.mock import patch, MagicMock

from src.agent.eternal_loop import EternalLoop


class TestEternalLoopInit(unittest.TestCase):
    """阶段36: 测试初始化状态。"""

    def test_initial_state(self):
        loop = EternalLoop()
        self.assertEqual(loop.run_counter, 0)
        self.assertTrue(loop.system_alive)
        self.assertEqual(loop.exception_count, 0)

    def test_clock_initialized(self):
        loop = EternalLoop()
        self.assertIsNotNone(loop.clock)
        self.assertGreaterEqual(loop.clock.elapsed(), 0)


class TestEternalLoopNormalRun(unittest.TestCase):
    """阶段37/42: 测试正常循环与计数器。"""

    def test_run_increments_counter(self):
        """循环应递增run_counter。"""
        loop = EternalLoop()
        # 用极短延时运行，通过设置system_alive=False来停止
        original_sleep = time.sleep

        def controlled_sleep(duration):
            if loop.run_counter >= 3:
                loop.system_alive = False
            original_sleep(0.01)

        with patch("src.agent.eternal_loop.time.sleep", side_effect=controlled_sleep):
            loop.run()

        self.assertEqual(loop.run_counter, 3)
        self.assertFalse(loop.system_alive)

    def test_loop_respects_system_alive(self):
        """system_alive=False时循环应立即停止。"""
        loop = EternalLoop()
        loop.system_alive = False

        with patch("src.agent.eternal_loop.time.sleep"):
            loop.run()

        self.assertEqual(loop.run_counter, 0)


class TestEternalLoopException(unittest.TestCase):
    """阶段38-39/40: 测试异常捕获与自愈。"""

    def test_exception_caught_and_counted(self):
        """异常应被捕获，exception_count递增，触发自愈。"""
        loop = EternalLoop()
        call_count = [0]
        original_sleep = time.sleep

        def inject_exception_on_second_cycle(duration):
            call_count[0] += 1
            if call_count[0] == 1:
                raise RuntimeError("模拟异常")
            if loop.run_counter >= 2:
                loop.system_alive = False
            original_sleep(0.01)

        with patch("src.agent.eternal_loop.time.sleep", side_effect=inject_exception_on_second_cycle):
            loop.run()

        self.assertGreaterEqual(loop.exception_count, 1)
        self.assertGreaterEqual(loop.run_counter, 1)

    def test_self_repair_resets_state(self):
        """self_repair应重置system_alive=True并重新运行。"""
        loop = EternalLoop()
        loop.system_alive = False
        loop.exception_count = 1

        repair_run_count = [0]
        original_sleep = time.sleep

        def stop_after_repair(duration):
            repair_run_count[0] += 1
            if loop.run_counter >= 2:
                loop.system_alive = False
            original_sleep(0.01)

        with patch("src.agent.eternal_loop.time.sleep", side_effect=stop_after_repair):
            loop.self_repair()

        # self_repair应将system_alive重置为True
        self.assertGreater(loop.run_counter, 0)


class TestEternalLoopSignal(unittest.TestCase):
    """阶段41: 测试信号处理与优雅退出。"""

    def test_sigint_sets_system_alive_false(self):
        """SIGINT信号应设置system_alive=False。"""
        loop = EternalLoop()
        original_sleep = time.sleep

        def send_sigint_and_stop(duration):
            if loop.run_counter >= 1:
                signal.raise_signal(signal.SIGINT)
            original_sleep(0.01)

        with patch("src.agent.eternal_loop.time.sleep", side_effect=send_sigint_and_stop):
            loop.run()

        self.assertFalse(loop.system_alive)
        self.assertGreaterEqual(loop.run_counter, 1)

    def test_sigterm_sets_system_alive_false(self):
        """SIGTERM信号应设置system_alive=False。"""
        loop = EternalLoop()
        original_sleep = time.sleep

        def send_sigterm_and_stop(duration):
            if loop.run_counter >= 1:
                signal.raise_signal(signal.SIGTERM)
            original_sleep(0.01)

        with patch("src.agent.eternal_loop.time.sleep", side_effect=send_sigterm_and_stop):
            loop.run()

        self.assertFalse(loop.system_alive)

    def test_signal_handlers_restored_after_run(self):
        """run结束后应恢复原始信号处理器。"""
        loop = EternalLoop()
        loop.system_alive = False

        with patch("src.agent.eternal_loop.time.sleep"):
            loop.run()

        # 验证原始handler被恢复（至少不再指向_handle_shutdown）
        current_handler = signal.getsignal(signal.SIGINT)
        self.assertNotEqual(current_handler, loop._handle_shutdown)


class TestEternalLoopHealthCheck(unittest.TestCase):
    """阶段43: 测试健康检查。"""

    def test_health_check_returns_dict(self):
        loop = EternalLoop()
        health = loop.health_check()
        self.assertIsInstance(health, dict)
        self.assertIn("uptime_seconds", health)
        self.assertIn("uptime_formatted", health)
        self.assertIn("run_counter", health)
        self.assertIn("exception_count", health)
        self.assertIn("system_alive", health)

    def test_health_check_reflects_state(self):
        loop = EternalLoop()
        loop.run_counter = 42
        loop.exception_count = 3
        health = loop.health_check()
        self.assertEqual(health["run_counter"], 42)
        self.assertEqual(health["exception_count"], 3)
        self.assertTrue(health["system_alive"])


class TestEternalLoopResourceCheck(unittest.TestCase):
    """阶段44: 测试资源熔断保护。"""

    def test_resource_check_no_warning_under_threshold(self):
        """内存低于阈值时不应记录警告。"""
        loop = EternalLoop()

        # mock resource.getrusage 返回远低于500MB的值
        mock_rusage = MagicMock()
        mock_rusage.ru_maxrss = 1024  # 1MB
        with patch("src.agent.eternal_loop.resource.getrusage", return_value=mock_rusage):
            with patch("src.agent.eternal_loop.logger") as mock_logger:
                loop.resource_check()
                mock_logger.warning.assert_not_called()

    def test_resource_check_warning_over_threshold(self):
        """内存超过阈值时应记录警告。"""
        loop = EternalLoop()

        # mock resource.getrusage 返回超过500MB的值 (ru_maxrss单位KB)
        mock_rusage = MagicMock()
        mock_rusage.ru_maxrss = 600 * 1024  # 600MB
        with patch("src.agent.eternal_loop.resource.getrusage", return_value=mock_rusage):
            with patch("src.agent.eternal_loop.logger") as mock_logger:
                loop.resource_check()
                mock_logger.warning.assert_called_once()
                warning_msg = mock_logger.warning.call_args[0][0]
                self.assertIn("资源熔断警告", warning_msg)


class TestEternalLoopIntegration(unittest.TestCase):
    """阶段45: 完整集成测试 - 正常循环→异常注入→自愈恢复→信号退出。"""

    def test_full_lifecycle(self):
        """
        完整生命周期测试：
        1. 正常循环3次
        2. 注入异常，触发自愈
        3. 自愈后再循环2次
        4. 发送SIGTERM退出
        """
        loop = EternalLoop()
        original_sleep = time.sleep
        phase = [0]  # 0=normal, 1=exception, 2=recovery, 3=exit

        def lifecycle_sleep(duration):
            if phase[0] == 0 and loop.run_counter >= 3:
                phase[0] = 1
            if phase[0] == 1:
                phase[0] = 2
                raise RuntimeError("集成测试: 模拟异常")
            if phase[0] == 2 and loop.run_counter >= 5:
                phase[0] = 3
            if phase[0] == 3 and loop.run_counter >= 5:
                signal.raise_signal(signal.SIGTERM)
            original_sleep(0.01)

        with patch("src.agent.eternal_loop.time.sleep", side_effect=lifecycle_sleep):
            loop.run()

        # 验证完整生命周期
        self.assertGreaterEqual(loop.run_counter, 3)
        self.assertGreaterEqual(loop.exception_count, 1)
        self.assertFalse(loop.system_alive)


if __name__ == "__main__":
    unittest.main()
