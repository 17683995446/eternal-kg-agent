# -*- coding: utf-8 -*-
"""
永动知识图谱 Agent - 路径管理模块
公理溯源: 记忆公理 - 路径管理确保记忆载体的物理位置可预测、可访问
设计原则: 统一管理所有文件路径，自动创建不存在的目录
"""

import os

from src.config import (
    KG_SAVE_PATH,
    LOG_FILE_PATH,
    TASK_QUEUE_SAVE_PATH,
)


class PathManager:
    """
    统一路径管理器。
    公理溯源: 记忆公理 - 所有数据文件的路径由此模块集中管理，
    确保记忆的物理存储位置一致且可预测。
    """

    def __init__(self, base_dir: str = None):
        """
        初始化路径管理器。
        公理溯源: 存续公理 - 基础目录的确定是系统启动的前提

        Args:
            base_dir: 项目根目录，默认为当前工作目录
        """
        if base_dir is None:
            base_dir = os.getcwd()
        self.base_dir = base_dir
        self.data_dir = os.path.join(base_dir, "data")

        # 确保数据目录存在
        os.makedirs(self.data_dir, exist_ok=True)

    @property
    def kg_path(self) -> str:
        """
        知识图谱持久化文件的完整路径。
        公理溯源: 记忆公理 - 知识图谱是系统的核心记忆载体
        """
        return os.path.join(self.base_dir, KG_SAVE_PATH)

    @property
    def task_queue_path(self) -> str:
        """
        任务队列持久化文件的完整路径。
        公理溯源: 自驱公理 - 任务队列是系统自驱动行为的待办清单
        """
        return os.path.join(self.base_dir, TASK_QUEUE_SAVE_PATH)

    @property
    def log_path(self) -> str:
        """
        日志文件的完整路径。
        公理溯源: 存续公理 - 日志记录系统运行状态，是存续监控的基础
        """
        return os.path.join(self.base_dir, LOG_FILE_PATH)

    def ensure_dirs(self) -> None:
        """
        确保所有必要的目录都已创建。
        公理溯源: 存续公理 - 目录存在是数据持久化的物理前提
        """
        for path in [self.kg_path, self.task_queue_path, self.log_path]:
            directory = os.path.dirname(path)
            if directory:
                os.makedirs(directory, exist_ok=True)
