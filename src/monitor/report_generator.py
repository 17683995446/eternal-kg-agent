# -*- coding: utf-8 -*-
"""
永动知识图谱 Agent - 运行报告生成模块
阶段90: 生成系统运行报告
公理溯源: 存续公理 - 报告是系统状态的可读化输出，便于人类审查
设计原则: 仅使用Python标准库，纯文本格式，信息密度高
"""

import os
import time

from src.clock import Clock
from src.config import SYSTEM_VERSION
from src.logger import get_logger

logger = get_logger("report_generator")


class ReportGenerator:
    """
    运行报告生成器。
    公理溯源: 存续公理 - 报告将系统内部状态转化为人类可读形式，
    是系统与外部世界沟通的桥梁。
    """

    def generate(self, metrics: dict, history_stats: dict = None,
                 health_score: float = 0.0) -> str:
        """
        生成运行报告字符串。
        公理溯源: 存续公理 - 报告生成是系统自我表达的过程

        Args:
            metrics: 指标数据
            history_stats: 执行历史统计
            health_score: 健康度评分

        Returns:
            格式化的报告字符串
        """
        lines = [
            "=" * 60,
            f"  永动知识图谱 Agent 运行报告",
            f"  版本: {SYSTEM_VERSION}",
            f"  生成时间: {Clock.format_timestamp()}",
            "=" * 60,
            "",
            "[系统指标]",
            f"  运行时长: {metrics.get('uptime_seconds', 0):.1f}秒",
            f"  循环次数: {metrics.get('loop_count', 0)}",
            f"  任务完成: {metrics.get('task_completed', 0)}",
            f"  任务失败: {metrics.get('task_failed', 0)}",
            f"  异常次数: {metrics.get('exception_count', 0)}",
            f"  内存占用: {metrics.get('memory_mb', 0):.1f}MB",
            f"  队列长度: {metrics.get('queue_size', 0)}",
            "",
        ]

        # 知识图谱统计
        kg_stats = metrics.get("kg_stats", {})
        if kg_stats:
            lines.extend([
                "[知识图谱]",
                f"  节点总数: {kg_stats.get('total_nodes', 0)}",
                f"  有效节点: {kg_stats.get('valid_nodes', 0)}",
                f"  边总数: {kg_stats.get('total_edges', 0)}",
                f"  平均权重: {kg_stats.get('avg_weight', 0):.4f}",
                "",
            ])

        # 执行历史统计
        if history_stats:
            lines.extend([
                "[执行历史]",
                f"  总执行数: {history_stats.get('total', 0)}",
                f"  平均耗时: {history_stats.get('avg_duration', 0):.4f}秒",
                f"  成功率: {history_stats.get('success_rate', 0) * 100:.1f}%",
                f"  衍生任务总数: {history_stats.get('total_derived', 0)}",
                "",
            ])

        # 健康度
        lines.extend([
            "[健康度]",
            f"  综合评分: {health_score:.1f}/100",
            f"  状态: {self._health_label(health_score)}",
            "",
            "=" * 60,
        ])

        return "\n".join(lines)

    def save_report(self, report: str,
                    save_path: str = "data/report.txt") -> str:
        """
        保存报告到文件。
        公理溯源: 记忆公理 - 报告持久化便于事后审查

        Args:
            report: 报告字符串
            save_path: 保存路径

        Returns:
            保存的文件路径
        """
        save_dir = os.path.dirname(save_path)
        if save_dir:
            os.makedirs(save_dir, exist_ok=True)

        with open(save_path, "w", encoding="utf-8") as f:
            f.write(report)

        logger.info(f"运行报告已保存: {save_path}")
        return save_path

    @staticmethod
    def _health_label(score: float) -> str:
        """
        根据健康度评分返回状态标签。
        公理溯源: 存续公理 - 标签将数值转化为直觉可理解的状态

        Args:
            score: 健康度评分

        Returns:
            状态标签字符串
        """
        if score >= 80:
            return "优秀"
        if score >= 60:
            return "良好"
        if score >= 40:
            return "一般"
        if score >= 20:
            return "较差"
        return "危险"
