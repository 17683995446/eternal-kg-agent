"""
基础配置管理模块

本模块实现配置信息的动态管理机制，支持配置的运行时读取和修改。
配置管理需要支持从环境变量读取配置的能力，允许通过环境变量覆盖默认配置值。
配置项按照功能模块进行分组管理，包括系统级配置、知识图谱配置、任务队列配置、自驱进化配置等。

设计原则：
- 零外部依赖：仅使用Python标准库
- 环境变量覆盖：支持通过环境变量动态调整配置
- 配置持久化：支持配置的序列化存储和反序列化加载
- 分组管理：按功能模块组织配置项
"""

import json
import os
from pathlib import Path

from config.constants import (
    LOOP_DELAY,
    HEALTH_CHECK_INTERVAL,
    MAX_RESTART_ATTEMPTS,
    REPAIR_SLEEP_DURATION,
    KG_SAVE_PATH,
    KG_VERSION,
    KG_AUTOSAVE_THRESHOLD,
    KG_BACKUP_ENABLED,
    KG_METADATA_ENABLED,
    EVOLVE_STEP,
    TASK_QUEUE_MAX,
    WEIGHT_THRESHOLD_HIGH,
    WEIGHT_THRESHOLD_LOW,
    WEIGHT_THRESHOLD_INVALID,
    WEIGHT_DECAY_RATE,
    WEIGHT_INCREMENT_TASK_DERIVE,
    WEIGHT_INCREMENT_TASK_SUCCESS,
    WEIGHT_MAX,
    WEIGHT_MIN,
    WEIGHT_INITIAL,
    LOG_LEVEL,
    LOG_FILE_ENABLED,
    LOG_MAX_SIZE,
    LOG_BACKUP_COUNT,
    RESOURCE_CPU_THRESHOLD,
    RESOURCE_MEMORY_THRESHOLD,
    RESOURCE_DISK_MIN_THRESHOLD,
    CIRCUIT_BREAKER_HIGH_DURATION,
    CIRCUIT_BREAKER_RECOVERY_DURATION,
    SYSTEM_VERSION,
)


class ConfigManager:
    """
    配置管理器

    统一管理所有系统配置项的存储和访问，支持环境变量覆盖和持久化。
    采用单例模式确保全系统只有一个配置管理器实例。

    Attributes:
        _config: 内部配置字典
        _config_file: 配置文件路径
        _initialized: 是否已初始化标志
    """

    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, config_file="config.json"):
        if ConfigManager._initialized:
            return

        self._config_file = Path(config_file)
        self._config = self._build_default_config()
        self._load_from_environment()
        self._load_from_file()

        ConfigManager._initialized = True

    def _build_default_config(self):
        """构建默认配置字典"""
        return {
            "system": {
                "version": SYSTEM_VERSION,
                "loop_delay": LOOP_DELAY,
                "health_check_interval": HEALTH_CHECK_INTERVAL,
                "max_restart_attempts": MAX_RESTART_ATTEMPTS,
                "repair_sleep_duration": REPAIR_SLEEP_DURATION,
            },
            "knowledge_graph": {
                "save_path": KG_SAVE_PATH,
                "version": KG_VERSION,
                "autosave_threshold": KG_AUTOSAVE_THRESHOLD,
                "backup_enabled": KG_BACKUP_ENABLED,
                "metadata_enabled": KG_METADATA_ENABLED,
            },
            "evolution": {
                "evolve_step": EVOLVE_STEP,
                "task_queue_max": TASK_QUEUE_MAX,
                "weight_threshold_high": WEIGHT_THRESHOLD_HIGH,
                "weight_threshold_low": WEIGHT_THRESHOLD_LOW,
                "weight_threshold_invalid": WEIGHT_THRESHOLD_INVALID,
                "weight_decay_rate": WEIGHT_DECAY_RATE,
                "weight_increment_task_derive": WEIGHT_INCREMENT_TASK_DERIVE,
                "weight_increment_task_success": WEIGHT_INCREMENT_TASK_SUCCESS,
                "weight_max": WEIGHT_MAX,
                "weight_min": WEIGHT_MIN,
                "weight_initial": WEIGHT_INITIAL,
            },
            "logging": {
                "level": LOG_LEVEL,
                "file_enabled": LOG_FILE_ENABLED,
                "max_size": LOG_MAX_SIZE,
                "backup_count": LOG_BACKUP_COUNT,
            },
            "resource": {
                "cpu_threshold": RESOURCE_CPU_THRESHOLD,
                "memory_threshold": RESOURCE_MEMORY_THRESHOLD,
                "disk_min_threshold": RESOURCE_DISK_MIN_THRESHOLD,
                "circuit_breaker_high_duration": CIRCUIT_BREAKER_HIGH_DURATION,
                "circuit_breaker_recovery_duration": CIRCUIT_BREAKER_RECOVERY_DURATION,
            },
        }

    def _load_from_environment(self):
        """从环境变量加载配置，覆盖默认值"""
        env_mappings = {
            "ETERNAL_KG_LOOP_DELAY": ("system", "loop_delay", float),
            "ETERNAL_KG_HEALTH_CHECK_INTERVAL": ("system", "health_check_interval", int),
            "ETERNAL_KG_MAX_RESTART_ATTEMPTS": ("system", "max_restart_attempts", int),
            "ETERNAL_KG_KG_SAVE_PATH": ("knowledge_graph", "save_path", str),
            "ETERNAL_KG_KG_AUTOSAVE_THRESHOLD": ("knowledge_graph", "autosave_threshold", int),
            "ETERNAL_KG_EVOLVE_STEP": ("evolution", "evolve_step", int),
            "ETERNAL_KG_TASK_QUEUE_MAX": ("evolution", "task_queue_max", int),
            "ETERNAL_KG_LOG_LEVEL": ("logging", "level", str),
            "ETERNAL_KG_CPU_THRESHOLD": ("resource", "cpu_threshold", float),
            "ETERNAL_KG_MEMORY_THRESHOLD": ("resource", "memory_threshold", float),
        }

        for env_var, (section, key, type_func) in env_mappings.items():
            value = os.environ.get(env_var)
            if value is not None:
                try:
                    self._config[section][key] = type_func(value)
                except (ValueError, TypeError):
                    pass

    def _load_from_file(self):
        """从配置文件加载配置，覆盖默认值和环境变量值"""
        if self._config_file.exists():
            try:
                with open(self._config_file, "r", encoding="utf-8") as f:
                    file_config = json.load(f)
                self._merge_config(file_config)
            except (json.JSONDecodeError, IOError):
                pass

    def _merge_config(self, file_config):
        """合并配置文件中的配置到当前配置"""
        for section, values in file_config.items():
            if section in self._config and isinstance(values, dict):
                self._config[section].update(values)

    def get(self, section, key=None, default=None):
        """
        获取配置项

        Args:
            section: 配置分组名称
            key: 配置项名称（可选，为None时返回整个分组）
            default: 默认值（当配置项不存在时返回）

        Returns:
            配置项值或默认值
        """
        if section not in self._config:
            return default

        if key is None:
            return self._config[section]

        return self._config[section].get(key, default)

    def set(self, section, key, value):
        """
        设置配置项

        Args:
            section: 配置分组名称
            key: 配置项名称
            value: 配置项值
        """
        if section not in self._config:
            self._config[section] = {}
        self._config[section][key] = value

    def get_system_config(self):
        """获取系统级配置"""
        return self._config.get("system", {})

    def get_knowledge_graph_config(self):
        """获取知识图谱配置"""
        return self._config.get("knowledge_graph", {})

    def get_evolution_config(self):
        """获取自驱进化配置"""
        return self._config.get("evolution", {})

    def get_logging_config(self):
        """获取日志配置"""
        return self._config.get("logging", {})

    def get_resource_config(self):
        """获取资源配置"""
        return self._config.get("resource", {})

    def save(self):
        """保存当前配置到配置文件"""
        try:
            with open(self._config_file, "w", encoding="utf-8") as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
            return True
        except IOError:
            return False

    def reload(self):
        """重新加载配置"""
        self._config = self._build_default_config()
        self._load_from_environment()
        self._load_from_file()

    def to_dict(self):
        """返回完整的配置字典"""
        return self._config.copy()

    def reset_to_defaults(self):
        """重置为默认配置"""
        self._config = self._build_default_config()


def get_config_manager():
    """
    获取配置管理器实例

    Returns:
        ConfigManager实例
    """
    return ConfigManager()
