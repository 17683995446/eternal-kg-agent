# -*- coding: utf-8 -*-
"""
永动知识图谱 Agent - 任务数据结构
阶段26: 定义任务的最小可识别单元
公理溯源:
  - 自驱公理: 任务是系统自驱行为的基本载体
  - 记忆公理: 任务携带创建时间与执行结果，构成行为记忆的时间线
设计原则: 仅使用标准库，支持序列化/反序列化以适配持久化需求
"""

import time
import uuid


class Task:
    """任务数据结构，携带唯一标识、优先级与状态。"""

    def __init__(
        self,
        name: str,
        description: str = "",
        priority: int = 0,
        task_id: str | None = None,
        created_at: float | None = None,
        status: str = "pending",
        result: str = "",
    ):
        self.id: str = task_id if task_id else uuid.uuid4().hex
        self.name: str = name
        self.description: str = description
        self.priority: int = priority
        self.created_at: float = created_at if created_at is not None else time.time()
        self.status: str = status
        self.result: str = result

    # ---- 序列化 ----

    def to_dict(self) -> dict:
        """将任务转为字典，用于JSON持久化。"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "priority": self.priority,
            "created_at": self.created_at,
            "status": self.status,
            "result": self.result,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """从字典恢复任务对象。"""
        return cls(
            task_id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            priority=data.get("priority", 0),
            created_at=data.get("created_at"),
            status=data.get("status", "pending"),
            result=data.get("result", ""),
        )

    def __repr__(self) -> str:
        return (
            f"Task(id={self.id!r}, name={self.name!r}, "
            f"priority={self.priority}, status={self.status!r})"
        )
