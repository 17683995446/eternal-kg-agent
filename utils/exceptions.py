"""
基础异常类层次结构设计

本模块为系统建立统一的异常处理框架，支撑存续公理中的"异常隔离"派生需求。
定义系统基础异常类作为所有系统自定义异常的基类，确保异常信息可追溯、可记录。

异常层次结构：
    SystemBaseException
        ├── KnowledgeGraphException
        │       ├── NodeException
        │       ├── EdgeException
        │       └── PersistenceException
        ├── TaskExecutionException
        │       ├── TaskQueueException
        │       └── TaskValidationException
        ├── SelfEvolutionException
        │       ├── DerivationException
        │       └── TrimException
        ├── ResourceException
        │       ├── ResourceExhaustedException
        │       └── CircuitBreakerException
        └── SystemStateException
"""


class SystemBaseException(Exception):
    """
    系统基础异常类

    所有系统自定义异常的基类，提供统一的异常信息结构和错误码管理。
    支持传入错误消息、错误码、原始异常对象等参数。

    Attributes:
        message: 错误描述消息
        error_code: 错误码，用于程序化处理
        original_exception: 原始异常对象（如果有）
        context: 异常发生时的上下文信息
    """

    ERROR_CODE = "SYS_001"
    ERROR_CATEGORY = "SYSTEM"

    def __init__(self, message, error_code=None, original_exception=None, context=None):
        """
        初始化基础异常

        Args:
            message: 错误描述消息
            error_code: 错误码，默认使用类属性ERROR_CODE
            original_exception: 原始异常对象（可选）
            context: 异常上下文信息字典（可选）
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.ERROR_CODE
        self.original_exception = original_exception
        self.context = context or {}

    def __str__(self):
        """返回格式化的异常信息"""
        parts = [f"[{self.error_code}] {self.message}"]
        if self.original_exception:
            parts.append(f"原始异常: {type(self.original_exception).__name__}: {self.original_exception}")
        if self.context:
            parts.append(f"上下文: {self.context}")
        return " | ".join(parts)

    def __repr__(self):
        """返回异常的repr表示"""
        return f"{self.__class__.__name__}(code={self.error_code}, message={self.message!r})"

    def to_dict(self):
        """
        将异常信息转换为字典格式

        Returns:
            包含异常信息的字典
        """
        return {
            "error_category": self.ERROR_CATEGORY,
            "error_code": self.error_code,
            "message": self.message,
            "exception_type": self.__class__.__name__,
            "original_exception": str(self.original_exception) if self.original_exception else None,
            "context": self.context,
        }


class KnowledgeGraphException(SystemBaseException):
    """
    知识图谱相关异常

    知识图谱操作过程中发生的异常，包括节点操作、边操作、持久化等。
    """

    ERROR_CODE = "KG_001"
    ERROR_CATEGORY = "KNOWLEDGE_GRAPH"


class NodeException(KnowledgeGraphException):
    """
    节点操作异常

    节点创建、查询、更新、删除过程中发生的异常。
    """

    ERROR_CODE = "KG_NODE_001"


class NodeNotFoundException(NodeException):
    """节点不存在异常"""

    ERROR_CODE = "KG_NODE_002"


class NodeAlreadyExistsException(NodeException):
    """节点已存在异常"""

    ERROR_CODE = "KG_NODE_003"


class NodeValidationException(NodeException):
    """节点数据验证异常"""

    ERROR_CODE = "KG_NODE_004"


class EdgeException(KnowledgeGraphException):
    """
    边操作异常

    边创建、查询、更新、删除过程中发生的异常。
    """

    ERROR_CODE = "KG_EDGE_001"


class EdgeNotFoundException(EdgeException):
    """边不存在异常"""

    ERROR_CODE = "KG_EDGE_002"


class EdgeAlreadyExistsException(EdgeException):
    """边已存在异常"""

    ERROR_CODE = "KG_EDGE_003"


class EdgeValidationException(EdgeException):
    """边数据验证异常"""

    ERROR_CODE = "KG_EDGE_004"


class PersistenceException(KnowledgeGraphException):
    """
    持久化操作异常

    数据保存、加载、备份过程中发生的异常。
    """

    ERROR_CODE = "KG_PERSIST_001"


class SaveException(PersistenceException):
    """数据保存异常"""

    ERROR_CODE = "KG_PERSIST_002"


class LoadException(PersistenceException):
    """数据加载异常"""

    ERROR_CODE = "KG_PERSIST_003"


class BackupException(PersistenceException):
    """数据备份异常"""

    ERROR_CODE = "KG_PERSIST_004"


class TaskExecutionException(SystemBaseException):
    """
    任务执行相关异常

    任务执行、调度、管理过程中发生的异常。
    """

    ERROR_CODE = "TASK_001"
    ERROR_CATEGORY = "TASK"


class TaskQueueException(TaskExecutionException):
    """任务队列异常"""

    ERROR_CODE = "TASK_QUEUE_001"


class TaskQueueFullException(TaskQueueException):
    """任务队列已满异常"""

    ERROR_CODE = "TASK_QUEUE_002"


class TaskQueueEmptyException(TaskQueueException):
    """任务队列为空异常"""

    ERROR_CODE = "TASK_QUEUE_003"


class TaskValidationException(TaskExecutionException):
    """任务验证异常"""

    ERROR_CODE = "TASK_VALID_001"


class TaskExecutionFailedException(TaskExecutionException):
    """任务执行失败异常"""

    ERROR_CODE = "TASK_EXEC_001"


class SelfEvolutionException(SystemBaseException):
    """
    自驱进化相关异常

    知识推演、进化、精简过程中发生的异常。
    """

    ERROR_CODE = "EVOLVE_001"
    ERROR_CATEGORY = "EVOLUTION"


class DerivationException(SelfEvolutionException):
    """知识推演异常"""

    ERROR_CODE = "EVOLVE_DERIVE_001"


class DerivationDepthException(DerivationException):
    """推演深度超限异常"""

    ERROR_CODE = "EVOLVE_DERIVE_002"


class TrimException(SelfEvolutionException):
    """知识精简异常"""

    ERROR_CODE = "EVOLVE_TRIM_001"


class ResourceException(SystemBaseException):
    """
    资源相关异常

    系统资源监控、管理过程中发生的异常。
    """

    ERROR_CODE = "RESOURCE_001"
    ERROR_CATEGORY = "RESOURCE"


class ResourceExhaustedException(ResourceException):
    """资源耗尽异常"""

    ERROR_CODE = "RESOURCE_EXHAUST_001"


class CircuitBreakerException(ResourceException):
    """熔断保护触发异常"""

    ERROR_CODE = "RESOURCE_CIRCUIT_001"


class SystemStateException(SystemBaseException):
    """
    系统状态异常

    系统状态管理、转换过程中发生的异常。
    """

    ERROR_CODE = "STATE_001"
    ERROR_CATEGORY = "SYSTEM_STATE"


class InvalidStateTransitionException(SystemStateException):
    """非法状态转换异常"""

    ERROR_CODE = "STATE_TRANS_001"


class SystemNotInitializedException(SystemStateException):
    """系统未初始化异常"""

    ERROR_CODE = "STATE_INIT_001"


class ConfigurationException(SystemBaseException):
    """
    配置相关异常

    配置读取、验证、应用过程中发生的异常。
    """

    ERROR_CODE = "CONFIG_001"
    ERROR_CATEGORY = "CONFIGURATION"


class ConfigNotFoundException(ConfigurationException):
    """配置项不存在异常"""

    ERROR_CODE = "CONFIG_NOT_FOUND_001"


class ConfigValidationException(ConfigurationException):
    """配置验证异常"""

    ERROR_CODE = "CONFIG_VALID_001"
