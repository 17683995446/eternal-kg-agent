"""
日志系统基础框架

本模块实现系统运行时的事件记录机制，满足存续公理中"可观测性"派生需求。
系统需要具备记录运行状态、捕获异常信息、追踪知识沉淀过程的能力。

设计原则：
- 零外部依赖：仅使用Python标准库logging模块
- 多级别日志输出：支持DEBUG、INFO、WARNING、ERROR、CRITICAL五级
- 双输出目的地：同时支持控制台和文件输出
- 自动轮转机制：防止日志文件无限膨胀
"""

import logging
import logging.handlers
import sys
from datetime import datetime
from pathlib import Path

from config.constants import (
    LOG_LEVEL,
    LOG_FILE_ENABLED,
    LOG_MAX_SIZE,
    LOG_BACKUP_COUNT,
    SYSTEM_NAME,
    SYSTEM_SHORT_NAME,
)


class Logger:
    """
    系统日志管理器

    提供统一的日志记录接口，支持多级别、多目的地、自动轮转等功能。
    所有系统组件通过此类实例记录日志，确保日志格式统一、管理集中。
    """

    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        """单例模式确保全系统只有一个日志管理器实例"""
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
        return cls._instance

    def __init__(self, name=None, log_level=None, log_file_enabled=None):
        """
        初始化日志管理器

        Args:
            name: 日志器名称，默认使用系统简称
            log_level: 日志级别，默认使用配置常量
            log_file_enabled: 是否启用文件日志，默认使用配置常量
        """
        if Logger._initialized:
            return

        self.name = name or SYSTEM_SHORT_NAME
        self.log_level = (log_level or LOG_LEVEL).upper()
        self.log_file_enabled = log_file_enabled if log_file_enabled is not None else LOG_FILE_ENABLED

        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(getattr(logging, self.log_level))
        self.logger.handlers = []

        self._setup_formatter()
        self._setup_console_handler()
        if self.log_file_enabled:
            self._setup_file_handler()

        Logger._initialized = True

    def _setup_formatter(self):
        """设置日志格式"""
        self.formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    def _setup_console_handler(self):
        """设置控制台输出处理器"""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, self.log_level))
        console_handler.setFormatter(self.formatter)
        self.logger.addHandler(console_handler)

    def _setup_file_handler(self):
        """设置文件输出处理器，支持自动轮转"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        log_file = log_dir / f"{SYSTEM_SHORT_NAME.lower()}.log"

        file_handler = logging.handlers.RotatingFileHandler(
            filename=str(log_file),
            maxBytes=LOG_MAX_SIZE,
            backupCount=LOG_BACKUP_COUNT,
            encoding="utf-8",
        )
        file_handler.setLevel(getattr(logging, self.log_level))
        file_handler.setFormatter(self.formatter)
        self.logger.addHandler(file_handler)

    def debug(self, message):
        """记录DEBUG级别日志"""
        self.logger.debug(message)

    def info(self, message):
        """记录INFO级别日志"""
        self.logger.info(message)

    def warning(self, message):
        """记录WARNING级别日志"""
        self.logger.warning(message)

    def error(self, message):
        """记录ERROR级别日志"""
        self.logger.error(message)

    def critical(self, message):
        """记录CRITICAL级别日志"""
        self.logger.critical(message)

    def log_event(self, event_type, message, level="INFO"):
        """
        记录结构化事件日志

        Args:
            event_type: 事件类型标识
            message: 事件描述
            level: 日志级别
        """
        formatted_message = f"[{event_type}] {message}"
        log_method = getattr(self, level.lower(), self.info)
        log_method(formatted_message)

    def log_knowledge_event(self, operation, node_name=None, edge_info=None):
        """
        记录知识图谱操作事件

        Args:
            operation: 操作类型（ADD_NODE、ADD_EDGE、UPDATE等）
            node_name: 节点名称（可选）
            edge_info: 边信息（可选）
        """
        message = f"知识操作: {operation}"
        if node_name:
            message += f" | 节点: {node_name}"
        if edge_info:
            message += f" | 边: {edge_info}"
        self.log_event("KNOWLEDGE", message)

    def log_task_event(self, task_name, status, details=None):
        """
        记录任务执行事件

        Args:
            task_name: 任务名称
            status: 任务状态（STARTED、COMPLETED、FAILED等）
            details: 附加详情（可选）
        """
        message = f"任务: {task_name} | 状态: {status}"
        if details:
            message += f" | 详情: {details}"
        self.log_event("TASK", message)

    def log_system_event(self, event, status="NORMAL"):
        """
        记录系统级事件

        Args:
            event: 事件描述
            status: 系统状态标识
        """
        message = f"系统事件: {event} | 状态: {status}"
        self.log_event("SYSTEM", message)

    def log_health_check(self, metrics):
        """
        记录健康检查结果

        Args:
            metrics: 健康指标字典
        """
        message = "健康检查 | " + " | ".join([f"{k}: {v}" for k, v in metrics.items()])
        self.log_event("HEALTH", message)

    def log_exception(self, exception, context=None):
        """
        记录异常信息

        Args:
            exception: 异常对象
            context: 异常发生时的上下文信息（可选）
        """
        message = f"异常: {type(exception).__name__}: {str(exception)}"
        if context:
            message += f" | 上下文: {context}"
        self.error(message)

    def set_level(self, level):
        """
        动态调整日志级别

        Args:
            level: 新的日志级别（DEBUG、INFO、WARNING、ERROR、CRITICAL）
        """
        self.log_level = level.upper()
        self.logger.setLevel(getattr(logging, self.log_level))
        for handler in self.logger.handlers:
            handler.setLevel(getattr(logging, self.log_level))

    def get_current_level(self):
        """获取当前日志级别"""
        return self.log_level


def get_logger(name=None):
    """
    获取日志管理器实例

    Args:
        name: 日志器名称（可选）

    Returns:
        Logger实例
    """
    return Logger(name)
