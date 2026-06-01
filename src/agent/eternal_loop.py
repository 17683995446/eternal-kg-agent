# -*- coding: utf-8 -*-
"""
永动知识图谱 Agent - 永续循环引擎
公理溯源: 存续公理 - 永续循环是系统持续存续的执行骨架
阶段36-44: 主循环骨架 / 节拍控制 / 异常捕获 / 自愈重启 / 信号退出 / 计数器 / 健康检查 / 资源熔断
设计原则: 仅使用Python标准库，代码简洁无冗余
"""

import signal
import time
import traceback
import resource

from src.config import LOOP_DELAY
from src.logger import get_logger
from src.clock import Clock

logger = get_logger("eternal_loop")


class EternalLoop:
    """
    永续循环引擎。
    公理溯源: 存续公理 - 循环是系统维持存续的核心节拍，
    每一次迭代都是系统"活着"的证明。
    """

    def __init__(self):
        """初始化永续循环引擎。"""
        self.run_counter = 0
        self.system_alive = True
        self.exception_count = 0
        self.clock = Clock()
        self._original_handlers = {}
        self._setup_signal_handlers()

    # ============================================================
    # 阶段41: 优雅退出信号处理
    # 公理溯源: 存续公理 - 优雅退出确保系统可被外部安全控制
    # ============================================================
    def _setup_signal_handlers(self):
        """注册SIGINT/SIGTERM信号处理器，收到信号后设置system_alive=False。"""
        for sig in (signal.SIGINT, signal.SIGTERM):
            self._original_handlers[sig] = signal.getsignal(sig)
            signal.signal(sig, self._handle_shutdown)

    def _handle_shutdown(self, signum, frame):
        """信号处理回调：标记系统停止。"""
        sig_name = signal.Signals(signum).name
        logger.info(f"收到信号 {sig_name}，系统将优雅退出")
        self.system_alive = False

    def _restore_signal_handlers(self):
        """恢复原始信号处理器。"""
        for sig, handler in self._original_handlers.items():
            signal.signal(sig, handler)

    # ============================================================
    # 阶段36-37: 主循环骨架 + 节拍控制
    # 阶段38-39: 全局异常捕获 + 异常日志
    # 阶段42: 运行计数器
    # ============================================================
    def run(self):
        """
        启动永续主循环。
        公理溯源: 存续公理 - while system_alive 循环是系统的心跳节拍
        """
        logger.info("永续循环引擎启动")
        try:
            while self.system_alive:
                self.run_counter += 1
                logger.debug(f"心跳 #{self.run_counter} | 运行时长: {self.clock.format_elapsed()}")
                self.resource_check()
                time.sleep(LOOP_DELAY)
        except Exception:
            self.exception_count += 1
            logger.error(f"循环异常: {traceback.format_exc()}")
            self.self_repair()
        finally:
            self._restore_signal_handlers()
            logger.info(f"永续循环引擎停止 | 总循环次数: {self.run_counter} | 异常次数: {self.exception_count}")

    # ============================================================
    # 阶段40: 自愈重启机制
    # 公理溯源: 存续公理 - 自愈能力确保系统从异常中恢复存续
    # ============================================================
    def self_repair(self):
        """
        自愈重启：短暂休眠后重置临时状态，尝试恢复运行。
        公理溯源: 存续公理 - 自愈是系统在异常后恢复存续的关键机制
        """
        logger.warning("自愈机制启动，正在恢复...")
        time.sleep(1)
        # 重置临时状态
        self.system_alive = True
        logger.info("自愈完成，系统已恢复")
        self.run()

    # ============================================================
    # 阶段43: 健康检查方法
    # 公理溯源: 存续公理 - 健康检查是系统感知自身存续状态的手段
    # ============================================================
    def health_check(self) -> dict:
        """
        检查核心健康指标。
        公理溯源: 存续公理 - 可量化的指标是判断系统存续质量的依据

        Returns:
            包含运行时长、循环次数、异常次数的字典
        """
        return {
            "uptime_seconds": round(self.clock.elapsed(), 2),
            "uptime_formatted": self.clock.format_elapsed(),
            "run_counter": self.run_counter,
            "exception_count": self.exception_count,
            "system_alive": self.system_alive,
        }

    # ============================================================
    # 阶段44: 资源熔断保护
    # 公理溯源: 存续公理 - 资源熔断防止系统因资源耗尽而终止存续
    # ============================================================
    def resource_check(self):
        """
        检查内存使用，超过阈值(500MB)时记录警告。
        公理溯源: 存续公理 - 资源监控是防止系统崩溃的最后防线
        """
        mem_mb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
        threshold_mb = 500
        if mem_mb > threshold_mb:
            logger.warning(f"资源熔断警告: 内存使用 {mem_mb:.1f}MB 超过阈值 {threshold_mb}MB")
