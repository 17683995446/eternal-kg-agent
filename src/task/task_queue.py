# -*- coding: utf-8 -*-
"""
永动知识图谱 Agent - 有限长度任务队列
阶段27-34: 实现带去重、持久化的有限长度任务队列
公理溯源:
  - 自驱公理: 任务队列是系统唯一驱动源，有限容量保障存续
  - 记忆公理: 持久化确保任务列表在系统重启后可恢复
  - 存续公理: 有限容量防止资源耗尽，保障系统持续运行
设计原则: 仅使用标准库（collections.deque, json, os），满队拒绝、重名拒绝
"""

import json
import os
from collections import deque

from src.config import TASK_QUEUE_MAX, TASK_QUEUE_SAVE_PATH
from src.logger import get_logger
from src.task.task import Task

logger = get_logger(__name__)


class TaskQueue:
    """有限长度任务队列，支持去重与JSON持久化。"""

    def __init__(self, max_size: int = TASK_QUEUE_MAX):
        self._queue: deque[Task] = deque()
        self._names: set[str] = set()
        self.max_size: int = max_size
        self._load()

    # ---- 入队操作 ----

    def add_task(self, task: Task) -> bool:
        """单个入队。满返回False，重名返回False，成功返回True。"""
        if task.name in self._names:
            logger.debug("任务重名被拒绝: %s", task.name)
            return False
        if len(self._queue) >= self.max_size:
            logger.warning("任务队列已满(%d)，拒绝: %s", self.max_size, task.name)
            return False
        self._queue.append(task)
        self._names.add(task.name)
        logger.debug("任务入队: %s", task.name)
        return True

    def batch_add_tasks(self, tasks: list[Task]) -> int:
        """批量入队，跳过重复与满队，返回实际入队数。"""
        count = 0
        for task in tasks:
            if self.add_task(task):
                count += 1
        return count

    # ---- 出队操作 ----

    def get_task(self) -> Task | None:
        """队首弹出，空返回None。"""
        if not self._queue:
            return None
        task = self._queue.popleft()
        self._names.discard(task.name)
        logger.debug("任务出队: %s", task.name)
        return task

    # ---- 状态查询 ----

    def is_empty(self) -> bool:
        return len(self._queue) == 0

    def is_full(self) -> bool:
        return len(self._queue) >= self.max_size

    @property
    def size(self) -> int:
        return len(self._queue)

    def peek(self) -> Task | None:
        """查看队首任务但不弹出，空返回None。"""
        return self._queue[0] if self._queue else None

    # ---- 持久化 ----

    def save(self) -> None:
        """将队列持久化到JSON文件。"""
        data = [task.to_dict() for task in self._queue]
        save_dir = os.path.dirname(TASK_QUEUE_SAVE_PATH)
        if save_dir:
            os.makedirs(save_dir, exist_ok=True)
        with open(TASK_QUEUE_SAVE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info("任务队列已持久化，共 %d 项", len(data))

    def _load(self) -> None:
        """从JSON文件恢复队列（内部方法，初始化时调用）。"""
        if not os.path.isfile(TASK_QUEUE_SAVE_PATH):
            return
        try:
            with open(TASK_QUEUE_SAVE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            for item in data:
                task = Task.from_dict(item)
                if task.name not in self._names:
                    self._queue.append(task)
                    self._names.add(task.name)
            logger.info("任务队列已恢复，共 %d 项", len(self._queue))
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logger.warning("任务队列恢复失败，将使用空队列: %s", e)

    # ---- 清空 ----

    def clear(self) -> None:
        """清空队列和去重集合。"""
        self._queue.clear()
        self._names.clear()
        logger.info("任务队列已清空")

    def __repr__(self) -> str:
        return f"TaskQueue(size={self.size}, max={self.max_size})"
