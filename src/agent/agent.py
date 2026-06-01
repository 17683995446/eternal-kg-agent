# -*- coding: utf-8 -*-
"""
永动知识图谱 Agent - 智能体核心主体
公理溯源:
  - 存续公理: 智能体通过永动循环维持自身存续，健康检查与自愈保障存续质量
  - 记忆公理: 知识图谱作为唯一长期记忆载体，任务执行沉淀为知识节点与关系
  - 自驱公理: 任务队列驱动系统行为，空闲时自主进化，执行时衍生新任务
阶段46-54: Agent骨架 / 初始化 / 获取任务 / 空闲进化 / 任务执行 / 知识沉淀 / 健康检查 / 自愈 / 永动循环
阶段76-85: 启动与初始认知 - 注入初始任务、种子知识、启动管理器集成
设计原则: 仅使用Python标准库，代码简洁无冗余
"""

import time
import traceback

from src.agent.eternal_loop import EternalLoop
from src.agent.startup import StartupManager
from src.clock import Clock
from src.config import EVOLVE_STEP, LOOP_DELAY
from src.kg.knowledge_graph import KnowledgeGraph
from src.logger import get_logger
from src.path_manager import PathManager
from src.task.task import Task
from src.task.task_queue import TaskQueue

logger = get_logger("agent")


class EternalSelfAgent:
    """
    永动自驱智能体。
    公理溯源: 三大公理交汇于此——
      存续公理: 永动循环维持系统持续运行，健康检查与自愈保障存续质量；
      记忆公理: 知识图谱记录每次任务执行的知识沉淀，形成持久记忆；
      自驱公理: 任务队列驱动系统行为，空闲时自主进化，执行时衍生新任务。
    """

    # ================================================================
    # 阶段46-47: Agent类骨架 + 初始化流程
    # 阶段76-85: 启动与初始认知集成
    # 公理溯源: 存续公理 - 初始化是系统从无到有的起点
    # ================================================================

    def __init__(self, base_dir: str = None):
        """
        初始化智能体，创建所有核心组件并加载持久化数据。
        公理溯源:
          存续公理 - Clock与logger提供系统感知能力
          记忆公理 - KnowledgeGraph加载历史记忆
          自驱公理 - TaskQueue加载待办任务

        Args:
            base_dir: 项目根目录，默认为当前工作目录（兼容阶段76-85启动流程）
        """
        self.path_manager = PathManager(base_dir)
        # 当未指定base_dir时，KnowledgeGraph和TaskQueue使用全局配置路径
        # 以兼容test_agent.py中的monkey-patch测试方式
        if base_dir is not None:
            self.knowledge_graph = KnowledgeGraph(save_path=self.path_manager.kg_path)
        else:
            self.knowledge_graph = KnowledgeGraph()
        self.kg = self.knowledge_graph  # 兼容别名
        self.task_queue = TaskQueue()
        self.clock = Clock()
        self.logger = logger
        self.run_counter = 0
        self.system_alive = True
        self.error_count = 0
        self._eternal_loop = EternalLoop()
        self.startup_manager = StartupManager(self.path_manager)

        self.logger.info(
            f"智能体初始化完成 | 图谱节点: {self.knowledge_graph.get_stats()['total_nodes']} "
            f"| 队列任务: {self.task_queue.size}"
        )

    # ================================================================
    # 阶段79: 注入初始任务
    # 公理溯源: 自驱公理 - 初始任务是系统自驱行为的起点
    # ================================================================

    def inject_initial_task(self) -> bool:
        """
        注入初始任务"系统初始认知迭代"。
        公理溯源: 自驱公理 - 初始任务是系统自驱行为的起点

        Returns:
            是否注入成功
        """
        task = Task(
            name="系统初始认知迭代",
            description="系统启动后的首次认知自检与知识图谱初始化",
            priority=10,
        )
        result = self.task_queue.add_task(task)
        if result:
            self.logger.info("初始任务已注入: 系统初始认知迭代")
        else:
            self.logger.info("初始任务已存在，跳过注入")
        return result

    # ================================================================
    # 阶段48: GET_CURRENT_TASK
    # 公理溯源: 自驱公理 - 获取任务是系统自驱行为的起点
    # ================================================================

    def get_current_task(self) -> Task | None:
        """
        从任务队列获取下一个待执行任务。
        公理溯源: 自驱公理 - 队列是系统行为的唯一驱动源

        Returns:
            Task实例或None（队列空时）
        """
        task = self.task_queue.get_task()
        if task is None:
            self.logger.debug("任务队列为空，无任务可执行")
        else:
            self.logger.debug(f"获取任务: {task.name}")
        return task

    # ================================================================
    # 阶段49: IDLE_SELF_EVOLVE
    # 公理溯源: 自驱公理 - 空闲时自主进化是系统自我提升的途径
    # ================================================================

    def idle_self_evolve(self) -> None:
        """
        无任务时执行空闲进化：遍历图谱节点统计、静默休眠。
        公理溯源:
          记忆公理 - 遍历图谱是对已有记忆的梳理与反思
          存续公理 - 静默休眠降低资源消耗，保障存续
        """
        stats = self.knowledge_graph.get_stats()
        self.logger.info(
            f"空闲进化 | 图谱统计: {stats['total_nodes']}节点, "
            f"{stats['total_edges']}边, 有效节点: {stats['valid_nodes']}"
        )
        time.sleep(LOOP_DELAY)

    # ================================================================
    # 阶段50-51: EXECUTE_TASK + 任务执行与知识沉淀联动
    # 公理溯源: 自驱公理(任务执行) + 记忆公理(知识沉淀)
    # ================================================================

    def execute_task(self, task: Task) -> None:
        """
        执行任务并将执行结果沉淀到知识图谱。
        公理溯源:
          自驱公理 - 任务执行是系统自驱行为的核心
          记忆公理 - 执行结果沉淀为知识节点与关系
          自驱公理 - 执行完毕后自主衍生下一迭代任务

        Args:
            task: 待执行的任务
        """
        self.logger.info(f"开始执行任务: {task.name}")

        # 将任务名作为节点存入图谱
        self.knowledge_graph.add_node(task.name)

        # 生成下一迭代任务名
        next_task_name = f"系统迭代任务_{self.run_counter}"

        # 创建"自主衍生"边：当前任务 -> 下一迭代任务
        self.knowledge_graph.add_edge(task.name, next_task_name, "自主衍生")

        # 将新任务入队
        next_task = Task(name=next_task_name, description=f"由任务'{task.name}'自主衍生")
        added = self.task_queue.add_task(next_task)
        if added:
            self.logger.debug(f"衍生任务已入队: {next_task_name}")
        else:
            self.logger.warning(f"衍生任务入队失败（队列满或重名）: {next_task_name}")

        # 保存图谱
        self.knowledge_graph.save()

        self.logger.info(f"任务执行完成: {task.name}")

    # ================================================================
    # 阶段52-53: HEALTH_CHECK + SELF_REPAIR
    # 公理溯源: 存续公理 - 健康检查与自愈保障系统存续质量
    # ================================================================

    def health_check(self) -> dict:
        """
        整合健康检查：EternalLoop状态 + 图谱状态 + 队列状态。
        公理溯源: 存续公理 - 全面的健康检查是感知系统存续状态的必要手段

        Returns:
            包含所有子系统健康指标的字典
        """
        loop_health = self._eternal_loop.health_check()
        kg_stats = self.knowledge_graph.get_stats()
        return {
            "uptime_seconds": loop_health["uptime_seconds"],
            "uptime_formatted": loop_health["uptime_formatted"],
            "run_counter": self.run_counter,
            "error_count": self.error_count,
            "system_alive": self.system_alive,
            "kg_nodes": kg_stats["total_nodes"],
            "kg_edges": kg_stats["total_edges"],
            "kg_valid_nodes": kg_stats["valid_nodes"],
            "queue_size": self.task_queue.size,
        }

    def self_repair(self) -> None:
        """
        执行自愈：调用EternalLoop的自愈逻辑，重置异常状态。
        公理溯源: 存续公理 - 自愈是系统从异常中恢复存续的关键机制
        """
        self.logger.warning("智能体自愈机制启动")
        self.error_count += 1
        time.sleep(1)
        self.system_alive = True
        self.logger.info("智能体自愈完成，系统已恢复")

    # ================================================================
    # 阶段54: ETERNAL_LOOP 终极循环
    # 公理溯源: 存续公理 - 永动循环是系统持续存续的终极执行骨架
    # ================================================================

    def eternal_loop(self) -> None:
        """
        永动主循环：整合所有方法的完整永动循环。
        公理溯源: 存续公理 - while system_alive 循环是系统心跳的终极节拍，
          每次迭代执行：健康检查→获取任务→执行/空闲进化→休眠，
          异常时触发自愈，每EVOLVE_STEP步触发知识精简提示。
        """
        self.logger.info("永动循环启动")

        while self.system_alive:
            try:
                # 健康检查
                self.health_check()

                # 获取任务
                task = self.get_current_task()

                if task is not None:
                    # 有任务：执行
                    self.run_counter += 1
                    self.execute_task(task)
                else:
                    # 无任务：空闲进化
                    self.idle_self_evolve()

                # 每EVOLVE_STEP步触发知识精简提示
                if self.run_counter > 0 and self.run_counter % EVOLVE_STEP == 0:
                    self.logger.info(
                        f"知识精简提示 | 已执行 {self.run_counter} 步 | "
                        f"图谱节点: {self.knowledge_graph.get_stats()['total_nodes']}"
                    )

                time.sleep(LOOP_DELAY)

            except Exception:
                self.logger.error(f"循环异常: {traceback.format_exc()}")
                self.self_repair()

        self.logger.info(
            f"永动循环停止 | 总执行步数: {self.run_counter} | 异常次数: {self.error_count}"
        )

    def run(self) -> None:
        """
        启动智能体主循环（兼容阶段76-85启动流程入口）。
        公理溯源: 存续公理 - 主循环是Agent持续存续的执行骨架
        """
        self.logger.info("永动自驱智能体启动")
        self._eternal_loop.run()

    def stop(self) -> None:
        """
        停止智能体（兼容阶段76-85启动流程入口）。
        公理溯源: 存续公理 - 停止是系统生命周期的终结
        """
        self._eternal_loop.system_alive = False
        self.logger.info("智能体停止信号已发送")
