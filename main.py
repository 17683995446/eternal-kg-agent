# -*- coding: utf-8 -*-
"""
永动知识图谱 Agent - 系统唯一启动入口
阶段76-85: 完整启动流程 - 自检、锁、注入、启动、关闭
公理溯源: 存续公理 - 入口是系统心跳的起点
设计原则: 极致精简，无冗余，可被三大公理解释
"""

import sys

from src.agent.agent import EternalSelfAgent
from src.agent.startup import StartupManager
from src.config import SYSTEM_VERSION
from src.logger import get_logger
from src.path_manager import PathManager

logger = get_logger("main")


def main():
    """系统启动入口。公理溯源: 存续公理 - main是系统生命的起点。"""
    logger.info(f"永动知识图谱 Agent v{SYSTEM_VERSION} 启动中...")

    # 初始化路径管理器
    path_manager = PathManager()

    # 初始化启动管理器
    startup = StartupManager(path_manager)

    # 阶段77: 启动自检
    if not startup.pre_launch_check():
        logger.error("启动自检失败，系统终止")
        sys.exit(1)

    # 阶段78: 多实例检测
    if startup.detect_existing_instance():
        logger.error("检测到已有实例运行，系统终止")
        sys.exit(1)

    try:
        # 创建Agent实例
        agent = EternalSelfAgent()

        # 阶段79: 注入初始任务
        agent.inject_initial_task()

        # 阶段80: 注入种子知识（冷启动）
        startup.inject_seed_knowledge(agent.kg)

        # 阶段81: 启动永动循环
        agent.run()

    except KeyboardInterrupt:
        logger.info("收到键盘中断")
    finally:
        # 阶段82: 优雅关闭
        startup.graceful_shutdown(agent.kg, agent.task_queue)


if __name__ == "__main__":
    main()
