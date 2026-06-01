# -*- coding: utf-8 -*-
"""
永动知识图谱 Agent - 知识进化器
阶段66-75: 知识进化与精简
公理溯源: 自驱公理 - 进化器执行完整的知识优化周期，
  通过衰减、修剪、归一化、备份实现知识的自我迭代
设计原则: 封装进化流程，提供可追溯的进化报告
"""

from src.kg.knowledge_graph import KnowledgeGraph
from src.logger import get_logger

logger = get_logger("evolution")


class KnowledgeEvolution:
    """
    知识进化器。
    公理溯源: 自驱公理 - 进化器编排完整的知识优化周期，
    是系统自我迭代的核心控制器。
    """

    def __init__(self, kg: KnowledgeGraph):
        """
        初始化进化器。

        Args:
            kg: 知识图谱实例
        """
        self.kg = kg

    def evolve(self, decay_factor: float = 0.95,
               trim_threshold: float = 0.1,
               backup_dir: str = "data/backups",
               max_backups: int = 5) -> dict:
        """
        执行完整进化周期：衰减 -> 修剪 -> 归一化 -> 备份 -> 报告。
        公理溯源: 自驱公理 - 完整进化周期是系统自我优化的标准流程

        Args:
            decay_factor: 衰减系数
            trim_threshold: 修剪阈值
            backup_dir: 备份目录
            max_backups: 最大备份数

        Returns:
            进化报告字典
        """
        report = {}
        report["before"] = self.kg.get_evolution_report()

        # 1. 衰减
        self.kg.decay_edges(decay_factor)
        logger.info(f"边权重衰减完成，系数={decay_factor}")

        # 2. 修剪
        trim_result = self.kg.trim_invalid_knowledge(trim_threshold)
        report["trim"] = trim_result
        logger.info(f"修剪完成: 删除{trim_result['edges_removed']}条边, "
                     f"{trim_result['nodes_removed']}个节点")

        # 3. 归一化
        self.kg.normalize_weights()
        logger.info("权重归一化完成")

        # 4. 备份
        backup_path = self.kg.backup_graph(backup_dir, max_backups)
        report["backup_path"] = backup_path

        # 5. 报告
        report["after"] = self.kg.get_evolution_report()
        report["evolution_success"] = True
        logger.info(f"进化周期完成: "
                     f"节点 {report['before']['total_nodes']} -> "
                     f"{report['after']['total_nodes']}, "
                     f"边 {report['before']['total_edges']} -> "
                     f"{report['after']['total_edges']}")
        return report
