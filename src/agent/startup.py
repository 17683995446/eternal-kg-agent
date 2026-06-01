# -*- coding: utf-8 -*-
"""
永动知识图谱 Agent - 启动管理器
阶段77-85: 系统启动自检 / 种子知识注入 / 多实例检测 / 优雅关闭
公理溯源: 存续公理 - 启动流程是系统从无到有的创世过程
设计原则: 仅使用Python标准库，确保启动过程可观测、可恢复
"""

import os
import time

from src.agent.instance_lock import InstanceLock
from src.clock import Clock
from src.config import SYSTEM_VERSION
from src.kg.knowledge_graph import KnowledgeGraph
from src.logger import get_logger
from src.path_manager import PathManager
from src.task.task import Task
from src.task.task_queue import TaskQueue

logger = get_logger("startup")

# 种子知识节点：冷启动时注入的初始认知
SEED_KNOWLEDGE = [
    {"name": "系统自身", "attr": {"type": "meta", "version": SYSTEM_VERSION}},
    {"name": "存续公理", "attr": {"type": "axiom", "desc": "系统必须持续运行以维持存在"}},
    {"name": "记忆公理", "attr": {"type": "axiom", "desc": "知识图谱是系统唯一长期记忆载体"}},
    {"name": "自驱公理", "attr": {"type": "axiom", "desc": "系统通过任务驱动自我演化"}},
    {"name": "永续循环", "attr": {"type": "component", "desc": "系统的心跳节拍引擎"}},
    {"name": "知识图谱", "attr": {"type": "component", "desc": "存储、检索、关联知识的核心结构"}},
    {"name": "任务队列", "attr": {"type": "component", "desc": "系统自驱动行为的待办清单"}},
]

# 种子知识边：定义初始认知间的关联
SEED_EDGES = [
    ("系统自身", "存续公理", "遵循"),
    ("系统自身", "记忆公理", "遵循"),
    ("系统自身", "自驱公理", "遵循"),
    ("永续循环", "存续公理", "实现"),
    ("知识图谱", "记忆公理", "实现"),
    ("任务队列", "自驱公理", "实现"),
]


class StartupManager:
    """
    启动管理器。
    公理溯源: 存续公理 - 启动管理器负责系统从静止到运行的完整过渡，
    确保所有前置条件满足、初始认知就位。
    """

    def __init__(self, path_manager: PathManager = None):
        """
        初始化启动管理器。

        Args:
            path_manager: 路径管理器实例，默认自动创建
        """
        self.path_manager = path_manager or PathManager()
        self.instance_lock = InstanceLock(
            lock_path=os.path.join(self.path_manager.data_dir, ".instance.lock")
        )
        self.clock = Clock()
        self._startup_errors: list[str] = []

    def pre_launch_check(self) -> bool:
        """
        启动自检：检查数据目录、文件权限。
        公理溯源: 存续公理 - 自检确保系统具备运行的基本条件

        Returns:
            True表示所有检查通过
        """
        self._startup_errors.clear()
        logger.info("启动自检开始")

        # 检查数据目录可写
        data_dir = self.path_manager.data_dir
        if not os.path.exists(data_dir):
            try:
                os.makedirs(data_dir, exist_ok=True)
                logger.info(f"数据目录已创建: {data_dir}")
            except OSError as e:
                self._startup_errors.append(f"数据目录创建失败: {e}")
                logger.error(f"数据目录创建失败: {e}")

        # 检查写入权限
        try:
            test_file = os.path.join(data_dir, ".write_test")
            with open(test_file, "w") as f:
                f.write("test")
            os.remove(test_file)
            logger.info("数据目录写入权限正常")
        except OSError as e:
            self._startup_errors.append(f"数据目录写入权限不足: {e}")
            logger.error(f"数据目录写入权限不足: {e}")

        # 检查持久化路径可达
        for path_name, path in [
            ("知识图谱", self.path_manager.kg_path),
            ("任务队列", self.path_manager.task_queue_path),
            ("日志文件", self.path_manager.log_path),
        ]:
            parent = os.path.dirname(path)
            if parent and not os.path.exists(parent):
                try:
                    os.makedirs(parent, exist_ok=True)
                except OSError as e:
                    self._startup_errors.append(f"{path_name}目录创建失败: {e}")

        if self._startup_errors:
            logger.error(f"启动自检失败: {self._startup_errors}")
            return False

        logger.info("启动自检通过")
        return True

    def inject_seed_knowledge(self, kg: KnowledgeGraph) -> int:
        """
        冷启动时注入种子知识节点。
        公理溯源: 记忆公理 - 种子知识是系统认知的初始锚点，
        为后续自驱演化提供语义基础

        Args:
            kg: 知识图谱实例

        Returns:
            实际注入的节点数（跳过已存在的）
        """
        injected = 0
        for seed in SEED_KNOWLEDGE:
            node = kg.get_node_by_name(seed["name"])
            if node is None:
                kg.add_node(seed["name"], attr=seed["attr"])
                injected += 1
                logger.debug(f"注入种子节点: {seed['name']}")

        for source, target, relation in SEED_EDGES:
            kg.add_edge(source, target, relation)
            logger.debug(f"注入种子边: {source} --[{relation}]--> {target}")

        if injected > 0:
            kg.save()
            logger.info(f"种子知识注入完成: {injected}个新节点")

        return injected

    def detect_existing_instance(self) -> bool:
        """
        通过锁文件检测是否已有实例运行。
        公理溯源: 存续公理 - 多实例检测防止并发写入导致记忆损坏

        Returns:
            True表示已有实例在运行
        """
        return not self.instance_lock.acquire()

    def graceful_shutdown(self, kg: KnowledgeGraph, task_queue: TaskQueue,
                         stats: dict = None) -> None:
        """
        优雅关闭：保存图谱、保存队列、输出统计。
        公理溯源: 存续公理 - 优雅关闭确保系统状态完整持久化，
        下次启动时可无缝恢复

        Args:
            kg: 知识图谱实例
            task_queue: 任务队列实例
            stats: 额外统计信息字典
        """
        logger.info("优雅关闭开始")

        # 保存知识图谱
        try:
            kg.save()
            logger.info("知识图谱已保存")
        except Exception as e:
            logger.error(f"知识图谱保存失败: {e}")

        # 保存任务队列
        try:
            task_queue.save()
            logger.info("任务队列已保存")
        except Exception as e:
            logger.error(f"任务队列保存失败: {e}")

        # 输出统计
        kg_stats = kg.get_stats()
        logger.info(
            f"关闭统计 | 运行时长: {self.clock.format_elapsed()} | "
            f"图谱节点: {kg_stats['total_nodes']} | "
            f"图谱边: {kg_stats['total_edges']} | "
            f"队列任务: {task_queue.size}"
        )

        if stats:
            for key, value in stats.items():
                logger.info(f"  {key}: {value}")

        # 释放实例锁
        self.instance_lock.release()
        logger.info("优雅关闭完成")
