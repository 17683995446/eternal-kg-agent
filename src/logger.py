# -*- coding: utf-8 -*-
"""
永动知识图谱 Agent - 日志模块
公理溯源: 存续公理 - 日志是系统感知自身状态的途径
设计原则: 零依赖，基于标准库logging，同时输出到控制台与文件
"""

import logging
import os

from src.config import LOG_FILE_PATH


def get_logger(name: str) -> logging.Logger:
    """
    获取命名Logger实例。
    公理溯源: 存续公理 - 统一日志接口确保系统各模块状态可观测

    Args:
        name: Logger名称，通常使用模块名

    Returns:
        配置好的Logger实例，同时输出到控制台和文件
    """
    logger = logging.getLogger(name)

    # 避免重复添加handler（同名logger可能被多次调用）
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # 日志格式: 时间 | 级别 | 模块 | 消息
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 控制台输出 (INFO及以上)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 文件输出 (DEBUG及以上，记录更详细的信息)
    log_dir = os.path.dirname(LOG_FILE_PATH)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
    file_handler = logging.FileHandler(LOG_FILE_PATH, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
