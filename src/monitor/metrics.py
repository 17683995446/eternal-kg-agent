# -*- coding: utf-8 -*-
"""
永动知识图谱 Agent - 指标采集模块
阶段86: 运行时长、循环次数、任务完成数、图谱大小、内存占用
公理溯源: 存续公理 - 指标是系统感知自身存续状态的量化手段
设计原则: 仅使用Python标准库，轻量级采集，无侵入
"""

import resource
import time

from src.logger import get_logger

logger = get_logger("metrics")


class MetricsCollector:
    """
    系统指标采集器。
    公理溯源: 存续公理 - 指标采集为系统提供自我感知能力，
    是判断系统健康状态的数据基础。
    """

    def __init__(self):
        """初始化指标采集器。"""
        self._start_time = time.time()
        self._loop_count = 0
        self._task_completed = 0
        self._task_failed = 0
        self._exception_count = 0

    def collect(self, kg_stats: dict = None, queue_size: int = 0) -> dict:
        """
        采集当前所有运行指标。
        公理溯源: 存续公理 - 采集是系统自我感知的核心动作

        Args:
            kg_stats: 知识图谱统计信息（来自KnowledgeGraph.get_stats()）
            queue_size: 当前任务队列长度

        Returns:
            包含所有指标的字典
        """
        mem_kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        mem_mb = mem_kb / 1024

        metrics = {
            "uptime_seconds": round(time.time() - self._start_time, 2),
            "loop_count": self._loop_count,
            "task_completed": self._task_completed,
            "task_failed": self._task_failed,
            "exception_count": self._exception_count,
            "memory_mb": round(mem_mb, 2),
            "kg_stats": kg_stats or {},
            "queue_size": queue_size,
        }
        return metrics

    def to_dict(self, kg_stats: dict = None, queue_size: int = 0) -> dict:
        """
        返回所有指标的字典（collect的别名）。
        公理溯源: 存续公理 - 统一接口便于上层模块使用
        """
        return self.collect(kg_stats, queue_size)

    def increment_loop(self) -> None:
        """递增循环计数。"""
        self._loop_count += 1

    def increment_task_completed(self) -> None:
        """递增任务完成计数。"""
        self._task_completed += 1

    def increment_task_failed(self) -> None:
        """递增任务失败计数。"""
        self._task_failed += 1

    def increment_exception(self) -> None:
        """递增异常计数。"""
        self._exception_count += 1
