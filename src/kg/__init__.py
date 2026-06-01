# -*- coding: utf-8 -*-
"""
永动知识图谱 Agent - 知识图谱模块
阶段11-75: Node/Edge数据结构、ID生成器、图谱核心、推演器、进化器
公理溯源: 记忆公理 - 知识图谱是系统唯一长期记忆载体
设计原则: 轻量级数据结构，支持CRUD、持久化、推演与进化
"""

from src.kg.edge import Edge
from src.kg.id_generator import generate_id
from src.kg.knowledge_graph import KnowledgeGraph
from src.kg.node import Node
from src.kg.task_deriver import TaskDeriver
from src.kg.evolution import KnowledgeEvolution

__all__ = [
    "Node", "Edge", "generate_id", "KnowledgeGraph",
    "TaskDeriver", "KnowledgeEvolution",
]
