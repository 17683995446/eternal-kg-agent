"""
文件操作工具函数

本模块实现文件系统相关的工具函数，支撑记忆公理中"本地文件持久化"的派生需求。
主要实现安全读取、安全写入、文件锁、目录创建等功能。

设计原则：
- 原子性写入：使用临时文件加重命名策略防止写入中断导致文件损坏
- 并发安全：文件锁机制防止并发写入导致的数据竞争
- 容错性：文件不存在时返回默认值而非抛出异常
"""

import fcntl
import json
import os
import tempfile
from pathlib import Path


def safe_read_file(filepath, default=None, encoding="utf-8"):
    """
    安全读取文件内容

    Args:
        filepath: 文件路径
        default: 文件不存在时的默认值
        encoding: 文件编码

    Returns:
        文件内容或默认值
    """
    try:
        with open(filepath, "r", encoding=encoding) as f:
            return f.read()
    except (IOError, OSError):
        return default


def safe_read_json(filepath, default=None, encoding="utf-8"):
    """
    安全读取JSON文件

    Args:
        filepath: 文件路径
        default: 文件不存在或解析失败时的默认值
        encoding: 文件编码

    Returns:
        解析后的JSON数据或默认值
    """
    try:
        with open(filepath, "r", encoding=encoding) as f:
            return json.load(f)
    except (IOError, OSError, json.JSONDecodeError):
        return default if default is not None else {}


def safe_write_file(filepath, content, encoding="utf-8"):
    """
    安全写入文件（原子性写入）

    使用临时文件加重命名的两步写入策略，确保写入的原子性。

    Args:
        filepath: 目标文件路径
        content: 要写入的内容
        encoding: 文件编码

    Returns:
        bool: 写入成功返回True，否则返回False
    """
    filepath = Path(filepath)
    try:
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding=encoding,
            dir=str(filepath.parent),
            prefix=f".{filepath.name}_tmp_",
            delete=False,
        ) as tmp_file:
            tmp_file.write(content)
            tmp_path = tmp_file.name

        os.replace(tmp_path, str(filepath))
        return True
    except (IOError, OSError):
        if "tmp_path" in locals():
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
        return False


def safe_write_json(filepath, data, encoding="utf-8", indent=2):
    """
    安全写入JSON文件（原子性写入）

    Args:
        filepath: 目标文件路径
        data: 要写入的JSON数据
        encoding: 文件编码
        indent: JSON缩进

    Returns:
        bool: 写入成功返回True，否则返回False
    """
    try:
        content = json.dumps(data, indent=indent, ensure_ascii=False)
        return safe_write_file(filepath, content, encoding)
    except (TypeError, ValueError):
        return False


def file_exists(filepath):
    """
    检查文件是否存在

    Args:
        filepath: 文件路径

    Returns:
        bool: 文件存在返回True
    """
    return Path(filepath).is_file()


def directory_exists(dirpath):
    """
    检查目录是否存在

    Args:
        dirpath: 目录路径

    Returns:
        bool: 目录存在返回True
    """
    return Path(dirpath).is_dir()


def ensure_directory_exists(dirpath):
    """
    确保目录存在，不存在则递归创建

    Args:
        dirpath: 目录路径

    Returns:
        bool: 目录存在或创建成功返回True
    """
    try:
        Path(dirpath).mkdir(parents=True, exist_ok=True)
        return True
    except OSError:
        return False


def get_file_size(filepath):
    """
    获取文件大小

    Args:
        filepath: 文件路径

    Returns:
        int: 文件大小（字节），文件不存在返回-1
    """
    try:
        return Path(filepath).stat().st_size
    except OSError:
        return -1


def get_file_meta(filepath):
    """
    获取文件元信息

    Args:
        filepath: 文件路径

    Returns:
        dict: 包含文件大小、创建时间、修改时间等属性的字典，文件不存在返回None
    """
    try:
        stat = Path(filepath).stat()
        return {
            "size": stat.st_size,
            "created_at": stat.st_ctime,
            "modified_at": stat.st_mtime,
            "accessed_at": stat.st_atime,
        }
    except OSError:
        return None


class FileLock:
    """
    文件锁机制

    防止并发写入导致的数据竞争，支持上下文管理器协议。

    Attributes:
        filepath: 锁文件路径
        _lock_file: 锁文件对象
    """

    def __init__(self, filepath):
        """
        初始化文件锁

        Args:
            filepath: 锁文件路径
        """
        self.filepath = Path(filepath)
        self._lock_file = None

    def acquire(self):
        """获取文件锁"""
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        self._lock_file = open(self.filepath, "w")
        fcntl.flock(self._lock_file.fileno(), fcntl.LOCK_EX)

    def release(self):
        """释放文件锁"""
        if self._lock_file:
            fcntl.flock(self._lock_file.fileno(), fcntl.LOCK_UN)
            self._lock_file.close()
            self._lock_file = None

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
        return False


def remove_file(filepath):
    """
    安全删除文件

    Args:
        filepath: 要删除的文件路径

    Returns:
        bool: 删除成功或文件不存在返回True
    """
    try:
        Path(filepath).unlink(missing_ok=True)
        return True
    except OSError:
        return False


def copy_file(src, dst):
    """
    复制文件

    Args:
        src: 源文件路径
        dst: 目标文件路径

    Returns:
        bool: 复制成功返回True
    """
    try:
        import shutil
        shutil.copy2(src, dst)
        return True
    except (IOError, OSError):
        return False


def list_files(dirpath, pattern="*"):
    """
    列出目录中的文件

    Args:
        dirpath: 目录路径
        pattern: 文件匹配模式

    Returns:
        list: 文件路径列表
    """
    try:
        return [str(p) for p in Path(dirpath).glob(pattern) if p.is_file()]
    except OSError:
        return []
