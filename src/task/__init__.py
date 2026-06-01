# -*- coding: utf-8 -*-
"""
永动知识图谱 Agent - 任务队列模块
公理溯源: 自驱公理 - 任务队列是系统唯一驱动源
设计原则: 封装Task数据结构与TaskQueue管理器
"""

from src.task.task import Task
from src.task.task_queue import TaskQueue

__all__ = ["Task", "TaskQueue"]
