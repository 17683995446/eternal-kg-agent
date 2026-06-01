# -*- coding: utf-8 -*-
"""
永动知识图谱 Agent - 知识推演器
阶段56-65: 知识推演与自驱
公理溯源: 自驱公理 - 推演器从已有知识中主动发现并生成新任务，
  实现系统的自驱行为闭环
设计原则: 封装推演逻辑，支持权重过滤、去重、多跳关联与优先级映射
"""

from src.kg.knowledge_graph import KnowledgeGraph
from src.logger import get_logger
from src.task.task import Task

logger = get_logger("task_deriver")


class TaskDeriver:
    """
    知识推演器。
    公理溯源: 自驱公理 - 推演器将知识图谱的关联关系转化为可执行任务，
    是系统自驱动力的核心引擎。
    """

    def __init__(self, kg: KnowledgeGraph):
        """
        初始化推演器。

        Args:
            kg: 知识图谱实例
        """
        self.kg = kg

    def _weight_to_priority(self, weight: float) -> int:
        """
        将边权重映射为任务优先级。
        公理溯源: 自驱公理 - 权重越高的关联越值得优先探索

        Args:
            weight: 边权重，范围[0.0, 1.0]

        Returns:
            优先级整数，权重越高优先级越大
        """
        return int(weight * 10)

    def derive_from_task(self, task_name: str,
                         weight_threshold: float = 0.2) -> list[Task]:
        """
        综合推演：从指定任务名出发，生成推演任务列表。
        公理溯源: 自驱公理 - 综合推演结合单跳与多跳发现，最大化知识扩展

        Args:
            task_name: 源任务/节点名称
            weight_threshold: 权重阈值

        Returns:
            Task对象列表（按优先级降序排列）
        """
        freq_control = self.kg.get_derive_frequency_control()

        # 频率控制：已推演节点跳过
        if task_name in freq_control:
            logger.debug(f"推演频率控制跳过: {task_name}")
            return []

        # 多跳推演获取任务名列表
        task_names = self.kg.derive_multi_hop_tasks(
            task_name, max_hops=2, weight_threshold=weight_threshold
        )

        # 收集边权重用于优先级映射
        source_node = self.kg.get_node_by_name(task_name)
        weight_map = {}
        if source_node:
            for edge in self.kg.edges:
                if edge.source_id == source_node.id:
                    target = self.kg.nodes.get(edge.target_id)
                    if target:
                        weight_map[target.name] = edge.weight

        # 构建Task对象
        tasks = []
        for name in task_names:
            target_name = name.replace("知识推演任务:", "")
            weight = weight_map.get(target_name, weight_threshold)
            priority = self._weight_to_priority(weight)
            tasks.append(Task(
                name=name,
                description=f"从[{task_name}]推演出的知识探索任务",
                priority=priority,
            ))

        # 按优先级降序排列
        tasks.sort(key=lambda t: t.priority, reverse=True)

        # 标记已推演
        freq_control.add(task_name)
        logger.info(f"推演完成: {task_name} -> {len(tasks)}个任务")
        return tasks
