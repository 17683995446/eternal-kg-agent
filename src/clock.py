# -*- coding: utf-8 -*-
"""
永动知识图谱 Agent - 系统时钟模块
公理溯源: 存续公理 - 时间是系统感知自身运行状态的维度
设计原则: 零依赖，基于标准库time，封装时间获取与运行时长统计
"""

import time


class Clock:
    """
    系统时钟。
    公理溯源: 存续公理 - 时钟为系统提供时间感知能力，
    是判断"系统已运行多久"的基础设施。
    """

    def __init__(self):
        """初始化时钟，记录启动时刻。"""
        self._start_time = time.time()

    def now(self) -> float:
        """
        获取当前Unix时间戳(秒)。
        公理溯源: 存续公理 - 精确的时间感知是系统调度的前提
        """
        return time.time()

    def elapsed(self) -> float:
        """
        获取自时钟创建以来的运行时长(秒)。
        公理溯源: 存续公理 - 运行时长是衡量系统存续状态的核心指标
        """
        return time.time() - self._start_time

    def format_elapsed(self) -> str:
        """
        将运行时长格式化为人类可读字符串，如 "01:23:45"。
        公理溯源: 记忆公理 - 可读的时间格式便于日志记录与人类审查
        """
        total_seconds = int(self.elapsed())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    @staticmethod
    def format_timestamp(ts: float = None) -> str:
        """
        将Unix时间戳格式化为可读字符串。
        公理溯源: 记忆公理 - 统一时间格式确保记忆的时间线一致

        Args:
            ts: Unix时间戳，默认为当前时间

        Returns:
            格式化后的时间字符串，如 "2024-01-01 12:00:00"
        """
        if ts is None:
            ts = time.time()
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts))
