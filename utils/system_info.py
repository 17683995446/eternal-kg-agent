"""
系统环境检测工具

本模块实现系统环境信息检测功能，为存续公理中的"资源管控"派生需求提供支撑。
需要实现系统资源检测功能、平台检测功能、依赖检测功能。

设计原则：
- 零外部依赖：仅使用Python标准库
- 跨平台：支持Windows、Linux、MacOS
- 低开销：检测操作不会显著影响系统性能
"""

import os
import platform
import sys


def get_cpu_usage():
    """
    获取CPU使用率

    Returns:
        float: CPU使用率百分比，获取失败返回-1.0
    """
    try:
        if hasattr(os, "getloadavg"):
            load_avg = os.getloadavg()[0]
            cpu_count = os.cpu_count() or 1
            return (load_avg / cpu_count) * 100.0
        return -1.0
    except (OSError, AttributeError):
        return -1.0


def get_memory_info():
    """
    获取内存使用情况

    Returns:
        dict: 包含total、available、percent等字段的字典，获取失败返回空字典
    """
    try:
        with open("/proc/meminfo", "r") as f:
            meminfo = f.read()

        mem_total = 0
        mem_available = 0

        for line in meminfo.split("\n"):
            if line.startswith("MemTotal:"):
                mem_total = int(line.split()[1]) * 1024
            elif line.startswith("MemAvailable:"):
                mem_available = int(line.split()[1]) * 1024

        if mem_total > 0:
            mem_used = mem_total - mem_available
            return {
                "total": mem_total,
                "available": mem_available,
                "used": mem_used,
                "percent": (mem_used / mem_total) * 100.0,
            }
        return {}
    except (IOError, OSError, ValueError):
        return {}


def get_disk_space(path="."):
    """
    获取磁盘空间信息

    Args:
        path: 要检查的目录路径

    Returns:
        dict: 包含total、used、free、percent等字段的字典，获取失败返回空字典
    """
    try:
        stat = os.statvfs(path)
        total = stat.f_blocks * stat.f_frsize
        free = stat.f_bavail * stat.f_frsize
        used = total - free
        return {
            "total": total,
            "used": used,
            "free": free,
            "percent": (used / total) * 100.0 if total > 0 else 0.0,
        }
    except (OSError, AttributeError):
        return {}


def get_process_id():
    """
    获取当前进程ID

    Returns:
        int: 当前进程ID
    """
    return os.getpid()


def get_platform():
    """
    获取当前操作系统平台

    Returns:
        str: 平台名称（windows、linux、darwin、unknown）
    """
    system = platform.system().lower()
    if system == "windows":
        return "windows"
    elif system == "linux":
        return "linux"
    elif system == "darwin":
        return "darwin"
    return "unknown"


def is_windows():
    """
    判断是否为Windows平台

    Returns:
        bool: 是Windows返回True
    """
    return get_platform() == "windows"


def is_linux():
    """
    判断是否为Linux平台

    Returns:
        bool: 是Linux返回True
    """
    return get_platform() == "linux"


def is_macos():
    """
    判断是否为MacOS平台

    Returns:
        bool: 是MacOS返回True
    """
    return get_platform() == "darwin"


def get_python_version():
    """
    获取Python版本信息

    Returns:
        str: Python版本字符串
    """
    return platform.python_version()


def check_external_dependencies():
    """
    检查是否存在外部依赖

    验证系统是否处于零外部依赖的纯净状态。

    Returns:
        dict: 包含has_external_dependencies和details字段的字典
    """
    external_modules = [
        "requests",
        "urllib3",
        "boto3",
        "redis",
        "pymongo",
        "psycopg2",
        "mysql",
        "sqlalchemy",
        "django",
        "flask",
        "fastapi",
        "numpy",
        "pandas",
    ]

    found = []
    for module in external_modules:
        try:
            __import__(module)
            found.append(module)
        except ImportError:
            pass

    return {
        "has_external_dependencies": len(found) > 0,
        "found_modules": found,
        "is_pure": len(found) == 0,
    }


def get_system_summary():
    """
    获取系统摘要信息

    Returns:
        dict: 包含系统各项信息的字典
    """
    return {
        "platform": get_platform(),
        "python_version": get_python_version(),
        "process_id": get_process_id(),
        "cpu_usage": get_cpu_usage(),
        "memory": get_memory_info(),
        "disk": get_disk_space(),
        "dependencies": check_external_dependencies(),
    }
