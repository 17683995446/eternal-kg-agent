# -*- coding: utf-8 -*-
"""
永动知识图谱 Agent - 执行历史记录模块
阶段88: 记录任务执行历史，支持持久化与查询
公理溯源: 记忆公理 - 执行历史是系统行为的时间线记忆
设计原则: 仅使用Python标准库，JSON格式持久化，支持最近N条查询
"""

import json
import os
import time

from src.logger import get_logger

logger = get_logger("execution_history")


class ExecutionHistory:
    """
    任务执行历史记录器。
    公理溯源: 记忆公理 - 执行历史为系统提供行为追溯能力，
    是分析系统演化轨迹的数据基础。
    """

    def __init__(self, save_path: str = "data/execution_history.json",
                 max_records: int = 1000):
        """
        初始化执行历史记录器。

        Args:
            save_path: 持久化文件路径
            max_records: 最大记录数，防止内存溢出
        """
        self._save_path = save_path
        self._max_records = max_records
        self._records: list[dict] = []
        self.load()

    def record(self, task_name: str, start_time: float, end_time: float,
               result: str, derived_count: int = 0) -> None:
        """
        记录一条任务执行历史。
        公理溯源: 记忆公理 - 每条记录是系统行为的一个时间点

        Args:
            task_name: 任务名称
            start_time: 开始时间戳
            end_time: 结束时间戳
            result: 执行结果
            derived_count: 衍生任务数
        """
        entry = {
            "task_name": task_name,
            "start_time": start_time,
            "end_time": end_time,
            "duration": round(end_time - start_time, 4),
            "result": result,
            "derived_count": derived_count,
            "recorded_at": time.time(),
        }
        self._records.append(entry)

        # 超过上限时淘汰最旧记录
        if len(self._records) > self._max_records:
            self._records = self._records[-self._max_records:]

        logger.debug(f"执行历史已记录: {task_name} (耗时{entry['duration']}s)")

    def get_recent(self, n: int = 10) -> list[dict]:
        """
        获取最近N条执行记录。
        公理溯源: 记忆公理 - 最近记录反映系统当前行为模式

        Args:
            n: 获取条数

        Returns:
            最近N条记录列表（按时间倒序）
        """
        return list(reversed(self._records[-n:]))

    @property
    def total_count(self) -> int:
        """总记录数。"""
        return len(self._records)

    def save(self) -> None:
        """
        持久化执行历史到文件。
        公理溯源: 记忆公理 - 持久化确保历史在系统重启后可恢复
        """
        save_dir = os.path.dirname(self._save_path)
        if save_dir:
            os.makedirs(save_dir, exist_ok=True)
        with open(self._save_path, "w", encoding="utf-8") as f:
            json.dump(self._records, f, ensure_ascii=False, indent=2)
        logger.info(f"执行历史已保存: {len(self._records)}条记录")

    def load(self) -> None:
        """
        从文件加载执行历史。
        公理溯源: 记忆公理 - 加载是系统启动时恢复历史记忆的步骤
        """
        if not os.path.exists(self._save_path):
            return
        try:
            with open(self._save_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                self._records = data[-self._max_records:]
                logger.info(f"执行历史已加载: {len(self._records)}条记录")
        except (json.JSONDecodeError, TypeError) as e:
            logger.warning(f"执行历史加载失败: {e}")

    def get_stats(self) -> dict:
        """
        获取执行历史统计。
        公理溯源: 存续公理 - 统计数据反映系统的行为特征

        Returns:
            包含总执行数、平均耗时、成功率的字典
        """
        if not self._records:
            return {
                "total": 0,
                "avg_duration": 0.0,
                "success_rate": 0.0,
                "total_derived": 0,
            }

        total = len(self._records)
        avg_duration = sum(r["duration"] for r in self._records) / total
        success_count = sum(1 for r in self._records if r["result"] != "failed")
        total_derived = sum(r["derived_count"] for r in self._records)

        return {
            "total": total,
            "avg_duration": round(avg_duration, 4),
            "success_rate": round(success_count / total, 4),
            "total_derived": total_derived,
        }
