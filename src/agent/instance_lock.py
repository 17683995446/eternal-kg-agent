# -*- coding: utf-8 -*-
"""
永动知识图谱 Agent - 实例锁模块
阶段76: 基于文件锁的多实例冲突检测
公理溯源: 存续公理 - 单实例运行保障系统状态的一致性与完整性
设计原则: 仅使用Python标准库(fcntl/msvcrt)，跨平台文件锁
"""

import os
import sys
import time

from src.logger import get_logger

logger = get_logger("instance_lock")

# 平台适配：Windows用msvcrt，Unix用fcntl
if sys.platform == "win32":
    import msvcrt
    _lock_func = msvcrt.locking
    _unlock_func = msvcrt.unlocking
    _LOCK_MODE = msvcrt.LK_NBLCK
else:
    import fcntl

    def _lock_func(fd, mode):
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)

    def _unlock_func(fd, mode):
        fcntl.flock(fd, fcntl.LOCK_UN)

    _LOCK_MODE = 1


class InstanceLock:
    """
    基于文件锁的多实例冲突检测。
    公理溯源: 存续公理 - 单实例约束防止多进程并发写入导致记忆损坏
    """

    def __init__(self, lock_path: str = "data/.instance.lock"):
        """
        初始化实例锁。

        Args:
            lock_path: 锁文件路径
        """
        self._lock_path = lock_path
        self._fd = None
        self._locked = False

    def acquire(self) -> bool:
        """
        尝试获取实例锁。
        公理溯源: 存续公理 - 获取锁是实例启动的必要前提

        Returns:
            True表示获取成功，False表示已被其他实例占用
        """
        lock_dir = os.path.dirname(self._lock_path)
        if lock_dir:
            os.makedirs(lock_dir, exist_ok=True)

        try:
            self._fd = open(self._lock_path, "w")
            _lock_func(self._fd.fileno(), _LOCK_MODE)
            self._fd.write(str(os.getpid()))
            self._fd.flush()
            self._locked = True
            logger.info(f"实例锁已获取: {self._lock_path} (PID={os.getpid()})")
            return True
        except (IOError, OSError) as e:
            if self._fd:
                self._fd.close()
                self._fd = None
            logger.warning(f"实例锁获取失败，可能已有实例运行: {e}")
            return False

    def release(self) -> None:
        """
        释放实例锁。
        公理溯源: 存续公理 - 释放锁是实例正常退出的必要步骤
        """
        if self._fd and self._locked:
            try:
                _unlock_func(self._fd.fileno(), _LOCK_MODE)
                self._fd.close()
                if os.path.exists(self._lock_path):
                    os.remove(self._lock_path)
                logger.info("实例锁已释放")
            except (IOError, OSError) as e:
                logger.warning(f"实例锁释放异常: {e}")
            finally:
                self._fd = None
                self._locked = False

    @property
    def is_locked(self) -> bool:
        """
        检查当前锁状态。
        公理溯源: 存续公理 - 锁状态查询是系统感知自身运行状态的手段
        """
        return self._locked

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
        return False
