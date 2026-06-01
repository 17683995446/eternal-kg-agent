# -*- coding: utf-8 -*-
"""
永动知识图谱 Agent - 健康度评分模块
阶段89: 综合计算0-100健康度评分
公理溯源: 存续公理 - 健康度是系统存续质量的量化指标
设计原则: 仅使用Python标准库，多维度加权评分
"""

import math


class HealthScorer:
    """
    系统健康度评分器。
    公理溯源: 存续公理 - 健康度评分将多维度指标综合为单一数值，
    便于快速判断系统存续状态。
    """

    def calculate(self, metrics: dict, history_stats: dict = None) -> float:
        """
        综合计算健康度评分(0-100)。
        公理溯源: 存续公理 - 多维度加权确保评分反映系统真实状态

        评分维度:
          - 任务完成率 (权重30%): 反映系统自驱效率
          - 知识质量 (权重25%): 反映记忆健康度
          - 异常频率 (权重25%): 反映系统稳定性
          - 资源占用 (权重20%): 反映资源使用合理性

        Args:
            metrics: 指标数据（来自MetricsCollector）
            history_stats: 执行历史统计（来自ExecutionHistory.get_stats()）

        Returns:
            0-100之间的健康度评分
        """
        scores = []

        # 维度1: 任务完成率 (权重30%)
        task_score = self._score_task_completion(metrics, history_stats)
        scores.append(("task_completion", task_score, 0.30))

        # 维度2: 知识质量 (权重25%)
        knowledge_score = self._score_knowledge_quality(metrics)
        scores.append(("knowledge_quality", knowledge_score, 0.25))

        # 维度3: 异常频率 (权重25%)
        exception_score = self._score_exception_rate(metrics)
        scores.append(("exception_rate", exception_score, 0.25))

        # 维度4: 资源占用 (权重20%)
        resource_score = self._score_resource_usage(metrics)
        scores.append(("resource_usage", resource_score, 0.20))

        # 加权求和
        total = sum(score * weight for _, score, weight in scores)
        return round(max(0.0, min(100.0, total)), 2)

    def _score_task_completion(self, metrics: dict,
                                history_stats: dict = None) -> float:
        """
        评估任务完成率。
        公理溯源: 自驱公理 - 任务完成率反映系统自驱效率
        """
        completed = metrics.get("task_completed", 0)
        failed = metrics.get("task_failed", 0)
        total = completed + failed

        if total == 0:
            # 没有任务执行记录，给予中性分
            return 70.0

        rate = completed / total
        return rate * 100

    def _score_knowledge_quality(self, metrics: dict) -> float:
        """
        评估知识图谱质量。
        公理溯源: 记忆公理 - 知识质量反映记忆的健康程度
        """
        kg_stats = metrics.get("kg_stats", {})
        total_nodes = kg_stats.get("total_nodes", 0)
        valid_nodes = kg_stats.get("valid_nodes", 0)
        total_edges = kg_stats.get("total_edges", 0)
        avg_weight = kg_stats.get("avg_weight", 0.0)

        if total_nodes == 0:
            return 50.0  # 空图谱，中性分

        # 有效节点比例
        validity_rate = valid_nodes / total_nodes

        # 连接密度（边数/节点数的对数，避免过大图惩罚）
        density = min(1.0, total_edges / max(1, total_nodes * math.log2(max(2, total_nodes))))

        # 权重合理性（0.3-0.7为理想区间）
        weight_score = 1.0 - abs(avg_weight - 0.5) * 2
        weight_score = max(0.0, weight_score)

        return (validity_rate * 40 + density * 30 + weight_score * 30)

    def _score_exception_rate(self, metrics: dict) -> float:
        """
        评估异常频率。
        公理溯源: 存续公理 - 异常频率反映系统稳定性
        """
        exceptions = metrics.get("exception_count", 0)
        loops = metrics.get("loop_count", 0)

        if loops == 0:
            return 100.0  # 没有循环，无异常

        rate = exceptions / loops
        # 异常率越低越好，线性映射
        return max(0.0, 100.0 - rate * 500)

    def _score_resource_usage(self, metrics: dict) -> float:
        """
        评估资源占用。
        公理溯源: 存续公理 - 资源占用反映系统运行效率
        """
        mem_mb = metrics.get("memory_mb", 0)

        # 100MB以下满分，500MB以上零分，线性插值
        if mem_mb <= 100:
            return 100.0
        if mem_mb >= 500:
            return 0.0
        return 100.0 - (mem_mb - 100) / 4
