# -*- coding: utf-8 -*-
"""
永动知识图谱 Agent - 智能体核心模块
阶段46-85: Agent骨架、永动循环、启动管理、实例锁
公理溯源: 三大公理交汇点 - 存续+记忆+自驱
设计原则: Agent是系统的心脏，协调所有子系统完成自驱循环
"""

from src.agent.agent import EternalSelfAgent
from src.agent.eternal_loop import EternalLoop
from src.agent.startup import StartupManager
from src.agent.instance_lock import InstanceLock

__all__ = ["EternalSelfAgent", "EternalLoop", "StartupManager", "InstanceLock"]
