"""
系统唯一启动入口

本模块实现系统的唯一启动入口main_entry函数，初始化智能体并启动主循环。
"""

import signal
import sys

from core.agent import EternalSelfAgent
from utils.logger import get_logger


logger = get_logger()
agent = None


def signal_handler(signum, frame):
    """信号处理函数"""
    global agent
    logger.log_system_event(f"收到信号 {signum}，准备关闭系统", "SIGNAL")
    if agent:
        agent.stop()
    sys.exit(0)


def main_entry():
    """
    系统唯一启动入口

    初始化智能体，注入初始根认知任务，启动自驱闭环原点。
    """
    global agent

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    logger.log_system_event("系统启动", "START")

    agent = EternalSelfAgent()
    agent.task_queue.add("系统初始认知迭代")

    logger.log_system_event("注入初始根认知任务", "INIT")

    try:
        agent.eternal_loop()
    except Exception as e:
        logger.log_exception(e, "系统异常退出")
        raise

    logger.log_system_event("系统正常关闭", "STOP")


if __name__ == "__main__":
    main_entry()
