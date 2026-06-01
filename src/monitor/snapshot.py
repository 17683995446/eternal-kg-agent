# -*- coding: utf-8 -*-
"""
永动知识图谱 Agent - 系统状态快照模块
阶段87: 生成与保存系统状态快照
公理溯源: 记忆公理 - 快照是系统状态在某一时刻的完整记忆
设计原则: 仅使用Python标准库，JSON格式持久化
"""

import json
import os
import time

from src.clock import Clock
from src.logger import get_logger

logger = get_logger("snapshot")


class SystemSnapshot:
    """
    系统状态快照。
    公理溯源: 记忆公理 - 快照记录系统在特定时刻的完整状态，
    便于事后分析与问题排查。
    """

    def __init__(self, save_dir: str = "data/snapshots"):
        """
        初始化快照管理器。

        Args:
            save_dir: 快照保存目录
        """
        self._save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)

    def take(self, metrics: dict, queue_size: int = 0,
             kg_stats: dict = None) -> dict:
        """
        生成系统状态快照。
        公理溯源: 记忆公理 - 快照是系统自我记忆的一种形式

        Args:
            metrics: 指标数据（来自MetricsCollector）
            queue_size: 当前队列长度
            kg_stats: 知识图谱统计

        Returns:
            快照字典
        """
        snapshot = {
            "timestamp": time.time(),
            "formatted_time": Clock.format_timestamp(),
            "metrics": metrics,
            "queue_size": queue_size,
            "kg_stats": kg_stats or {},
        }
        logger.debug(f"系统快照已生成: {snapshot['formatted_time']}")
        return snapshot

    def save(self, snapshot: dict) -> str:
        """
        保存快照到文件。
        公理溯源: 记忆公理 - 持久化确保快照可被事后检索

        Args:
            snapshot: 快照字典

        Returns:
            保存的文件路径
        """
        ts = snapshot.get("formatted_time", Clock.format_timestamp())
        filename = f"snapshot_{ts.replace(' ', '_').replace(':', '-')}.json"
        filepath = os.path.join(self._save_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(snapshot, f, ensure_ascii=False, indent=2)

        logger.info(f"快照已保存: {filepath}")
        return filepath
