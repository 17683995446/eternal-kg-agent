"""
时间管理工具函数

本模块实现时间相关的工具函数库，支撑记忆公理中"时间戳记录"的派生需求。
这些工具函数需要具有高性能和低开销的特点，因为它们会在系统主循环中频繁调用。

设计原则：
- 高性能：最小化时间计算的开销
- 高精度：满足毫秒级时间精度要求
- 标准化：统一使用Unix时间戳格式
"""

import time
import random
from datetime import datetime, timezone


def get_timestamp():
    """
    获取当前Unix时间戳（秒）

    Returns:
        float: 当前Unix时间戳，精确到小数点后6位（微秒级）
    """
    return time.time()


def get_timestamp_ms():
    """
    获取当前Unix时间戳（毫秒）

    Returns:
        int: 当前Unix时间戳的毫秒表示
    """
    return int(time.time() * 1000)


def get_formatted_time(timestamp=None, fmt="%Y-%m-%d %H:%M:%S"):
    """
    获取格式化时间字符串

    Args:
        timestamp: Unix时间戳（可选，默认当前时间）
        fmt: 时间格式字符串（默认"%Y-%m-%d %H:%M:%S"）

    Returns:
        str: 格式化后的时间字符串
    """
    if timestamp is None:
        timestamp = time.time()
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime(fmt)


def get_iso_time(timestamp=None):
    """
    获取ISO 8601格式的时间字符串

    Args:
        timestamp: Unix时间戳（可选，默认当前时间）

    Returns:
        str: ISO 8601格式的时间字符串
    """
    if timestamp is None:
        timestamp = time.time()
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat()


def time_diff(start_time, end_time=None):
    """
    计算两个时间点之间的秒数差

    Args:
        start_time: 起始时间戳
        end_time: 结束时间戳（可选，默认当前时间）

    Returns:
        float: 时间差（秒），正数表示start_time在end_time之前
    """
    if end_time is None:
        end_time = time.time()
    return end_time - start_time


def time_diff_ms(start_time_ms, end_time_ms=None):
    """
    计算两个时间点之间的毫秒差

    Args:
        start_time_ms: 起始时间戳（毫秒）
        end_time_ms: 结束时间戳（毫秒）（可选，默认当前时间）

    Returns:
        int: 时间差（毫秒）
    """
    if end_time_ms is None:
        end_time_ms = get_timestamp_ms()
    return end_time_ms - start_time_ms


def is_period_elapsed(last_time, period_seconds):
    """
    判断自上次时间起是否已超过指定周期

    Args:
        last_time: 上次执行的时间戳
        period_seconds: 周期时长（秒）

    Returns:
        bool: 若已超过周期返回True，否则返回False
    """
    return time.time() - last_time >= period_seconds


def is_step_elapsed(counter, step):
    """
    判断计数器是否达到固定步数

    Args:
        counter: 当前计数器值
        step: 目标步数

    Returns:
        bool: 若counter % step == 0且counter > 0返回True
    """
    return counter > 0 and counter % step == 0


def generate_unique_id():
    """
    生成唯一时间标识

    基于时间戳和随机数生成不重复ID，格式：timestamp_random

    Returns:
        str: 唯一标识符
    """
    timestamp = int(time.time() * 1000)
    random_suffix = random.randint(1000, 9999)
    return f"{timestamp}_{random_suffix}"


def generate_short_id():
    """
    生成短唯一标识

    基于时间戳生成较短的唯一标识

    Returns:
        str: 短唯一标识符
    """
    return f"{int(time.time() * 1000):x}"


def sleep(seconds):
    """
    休眠指定秒数

    Args:
        seconds: 休眠时长（秒）
    """
    time.sleep(seconds)


def get_current_year():
    """
    获取当前年份

    Returns:
        int: 当前年份
    """
    return datetime.now(timezone.utc).year


def get_current_month():
    """
    获取当前月份

    Returns:
        int: 当前月份（1-12）
    """
    return datetime.now(timezone.utc).month


def get_current_day():
    """
    获取当前日期

    Returns:
        int: 当前日期（1-31）
    """
    return datetime.now(timezone.utc).day


def timestamp_to_datetime(timestamp):
    """
    将Unix时间戳转换为datetime对象

    Args:
        timestamp: Unix时间戳

    Returns:
        datetime: UTC时区的datetime对象
    """
    return datetime.fromtimestamp(timestamp, tz=timezone.utc)


def datetime_to_timestamp(dt):
    """
    将datetime对象转换为Unix时间戳

    Args:
        dt: datetime对象

    Returns:
        float: Unix时间戳
    """
    return dt.timestamp()
