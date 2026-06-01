"""
智能体核心逻辑

本模块实现系统的核心运行主体EternalSelfAgent，整合知识图谱和其他系统组件，
控制主循环的执行逻辑，协调任务执行和知识沉淀。
"""

import time
import traceback

from config.constants import (
    LOOP_DELAY,
    EVOLVE_STEP,
    TASK_QUEUE_MAX,
    MAX_RESTART_ATTEMPTS,
    REPAIR_SLEEP_DURATION,
    SYSTEM_ALIVE_FLAG,
    RELATION_DERIVED,
)
from models.knowledge_graph import KnowledgeGraph
from utils.data_structures import FixedQueue
from utils.time_utils import sleep, get_timestamp
from utils.logger import get_logger


class EternalSelfAgent:
    """
    永续自治智能体

    系统的核心运行主体，负责整合知识图谱、控制主循环、协调任务执行。

    Attributes:
        knowledge_graph: 知识图谱实例
        task_queue: 任务队列
        run_counter: 运行计数器
        system_alive: 系统存活标志
        restart_count: 重启计数器
    """

    def __init__(self, knowledge_graph=None):
        """
        初始化智能体

        Args:
            knowledge_graph: 知识图谱实例（可选）
        """
        self.knowledge_graph = knowledge_graph or KnowledgeGraph()
        self.task_queue = FixedQueue(TASK_QUEUE_MAX)
        self.run_counter = 0
        self.system_alive = True
        self.restart_count = 0
        self.logger = get_logger()

        self.logger.log_system_event("智能体初始化完成", "NORMAL")

    def health_check(self):
        """
        健康检查

        检查系统状态，周期性触发知识进化。
        """
        self.run_counter += 1

        if self.run_counter % EVOLVE_STEP == 0:
            self.logger.log_system_event(f"触发知识进化 (步数: {self.run_counter})", "EVOLVE")
            removed_edges, removed_nodes = self.knowledge_graph.trim_invalid_knowledge()
            self.logger.log_system_event(
                f"知识进化完成: 移除{removed_edges}条边, {removed_nodes}个节点", "EVOLVE"
            )

    def self_repair(self):
        """
        自愈恢复

        在系统遇到异常时执行恢复操作。
        """
        self.logger.log_system_event("执行自愈恢复", "REPAIR")
        self.restart_count += 1

        if self.restart_count > MAX_RESTART_ATTEMPTS:
            self.logger.log_system_event("超过最大重启次数，系统停止", "CRITICAL")
            self.system_alive = False
            return

        sleep(REPAIR_SLEEP_DURATION)
        self.logger.log_system_event("自愈恢复完成", "REPAIR")

    def get_current_task(self):
        """
        获取当前待执行任务

        Returns:
            str: 任务描述，队列为空返回None
        """
        return self.task_queue.get()

    def idle_self_evolve(self):
        """
        空闲自进化

        任务队列为空时自动调用，执行空闲时期的进化行为。
        """
        self.logger.log_system_event("系统空闲，执行自进化", "IDLE")

        if self.knowledge_graph.nodes:
            nodes = list(self.knowledge_graph.nodes.values())
            for node in nodes[:3]:
                derived = self.knowledge_graph.derive_new_tasks(node.node_name)
                for task in derived[:2]:
                    self.task_queue.add(task)

        self.task_queue.add("系统迭代任务_空闲")

    def execute_task(self, task):
        """
        执行任务

        Args:
            task: 任务描述字符串
        """
        self.logger.log_task_event(task, "STARTED")

        derive_tasks = self.knowledge_graph.derive_new_tasks(task)

        node = self.knowledge_graph.add_node(task)
        node.activate()

        next_iter_task = f"系统迭代任务_{self.run_counter}"
        next_node = self.knowledge_graph.add_node(next_iter_task)

        self.knowledge_graph.add_edge(
            task, next_iter_task, RELATION_DERIVED, weight=0.8
        )

        self.task_queue.add(next_iter_task)
        self.task_queue.batch_add(derive_tasks)

        self.logger.log_task_event(task, "COMPLETED", f"衍生{len(derive_tasks)}个新任务")

    def eternal_loop(self):
        """
        永恒主循环

        系统的心脏，永不退出的主循环。
        """
        self.logger.log_system_event("启动永恒主循环", "LOOP")

        while self.system_alive:
            try:
                self.health_check()
                task = self.get_current_task()

                if task is None:
                    self.idle_self_evolve()
                    sleep(LOOP_DELAY)
                    continue

                self.execute_task(task)
                sleep(LOOP_DELAY)

            except Exception as e:
                self.logger.log_exception(e, "主循环异常")
                self.self_repair()

        self.logger.log_system_event("永恒主循环结束", "STOP")

    def stop(self):
        """停止系统"""
        self.system_alive = False
        self.knowledge_graph.save()
        self.logger.log_system_event("系统停止", "STOP")

    def __repr__(self):
        return f"EternalSelfAgent(run_counter={self.run_counter}, tasks={self.task_queue.size()})"
