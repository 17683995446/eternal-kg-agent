# 永动知识图谱 Agent (Eternal Agent)

基于第一性原理的轻量化永动知识图谱Agent系统，零外部依赖，100阶段完整实现。

## 项目简介与设计理念

本项目从三大公理出发，构建一个能够自主运行、积累记忆、自我驱动的Agent系统。系统以知识图谱为核心记忆载体，以任务队列为行为驱动源，以永续循环为心跳节拍，实现了从启动、运行、进化到优雅关闭的完整生命周期。

**核心理念：**
- 第一性原理驱动：所有设计决策均可追溯到三大公理
- 零外部依赖：仅使用Python标准库
- 极致精简：无冗余代码，每行都可被公理解释
- 公理溯源：每个模块、每个常量都标注其公理来源

## 三大公理

本系统的所有设计决策均可追溯到以下三大公理：

### 1. 存续公理 (Axiom of Survival)
系统必须维持自身的持续运行。一切设计以系统存续为第一优先级。
- 体现：主循环(EternalLoop)、日志监控(Logger)、异常恢复(SelfRepair)、资源熔断(ResourceCheck)、实例锁(InstanceLock)、启动自检(PreLaunchCheck)

### 2. 记忆公理 (Axiom of Memory)
系统必须积累和利用历史经验。没有记忆的系统无法进化。
- 体现：知识图谱(KnowledgeGraph)持久化、任务队列(TaskQueue)、日志记录(Logger)、时间线追踪(Clock)、执行历史(ExecutionHistory)、系统快照(Snapshot)

### 3. 自驱公理 (Axiom of Self-Drive)
系统必须能够自主产生目标和行为。被动响应不足以构成Agent。
- 体现：任务生成(TaskDeriver)、知识进化(KnowledgeEvolution)、自迭代循环(EternalLoop)、版本演进(SYSTEM_VERSION)、推演频率控制

## 系统架构图（文字版）

```
+------------------------------------------------------------------+
|                        main.py (启动入口)                         |
|  启动自检 -> 多实例检测 -> 创建Agent -> 注入初始任务 -> 注入种子知识  |
|  -> 启动永动循环 -> 优雅关闭                                       |
+------------------------------------------------------------------+
           |                              |
    +------v--------+            +--------v--------+
    | StartupManager |            | EternalSelfAgent|
    | - pre_launch   |            | - eternal_loop  |
    | - seed_knowledge|           | - execute_task  |
    | - shutdown     |            | - idle_evolve   |
    +----------------+            | - health_check  |
                                  | - self_repair   |
                                  +--------+--------+
                                           |
                    +----------------------+----------------------+
                    |                      |                      |
           +--------v--------+   +--------v--------+   +--------v--------+
           | KnowledgeGraph  |   |   TaskQueue     |   |   EternalLoop   |
           | - add_node/edge |   | - add_task      |   | - run          |
           | - derive_tasks  |   | - get_task      |   | - self_repair  |
           | - evolve/trim  |   | - save/load     |   | - health_check |
           | - save/load    |   | - batch_add     |   | - signal_exit  |
           +--------+--------+   +----------------+   +----------------+
                    |
           +--------v--------+
           |  TaskDeriver    |
           | - derive_from  |
           +----------------+
                    |
           +--------v--------+
           | KnowledgeEvolution|
           | - decay/trim     |
           | - normalize      |
           | - backup         |
           +-----------------+

           +------------------------------------------+
           |            监控子系统 (Monitor)             |
           | MetricsCollector | SystemSnapshot          |
           | ExecutionHistory | HealthScorer           |
           | ReportGenerator                            |
           +------------------------------------------+

           +------------------------------------------+
           |            基础设施 (Infrastructure)       |
           | Clock | Logger | PathManager | Config      |
           +------------------------------------------+
```

## 目录结构说明

```
eternal-agent/
  main.py                    # 系统唯一启动入口（阶段76-85）
  requirements.txt           # 依赖清单（空，体现零依赖原则）
  README.md                  # 项目说明文档
  .gitignore                 # Git忽略配置
  src/                       # 源代码包
    __init__.py              # 包初始化
    config.py                # 全局常量配置（公理溯源标注）
    logger.py                # 日志模块（控制台+文件双输出）
    clock.py                 # 系统时钟（时间感知与运行时长）
    path_manager.py          # 路径管理（统一管理数据文件路径）
    kg/                      # 知识图谱模块（阶段11-75）
      __init__.py
      node.py                # 节点数据结构
      edge.py                # 边数据结构
      id_generator.py        # 唯一ID生成器
      knowledge_graph.py     # 图谱核心类（CRUD+持久化+推演+进化）
      task_deriver.py        # 知识推演器（自驱引擎）
      evolution.py           # 知识进化器（衰减/修剪/归一化/备份）
    task/                    # 任务管理模块（阶段26-35）
      __init__.py
      task.py                # 任务数据结构
      task_queue.py          # 有限长度任务队列（去重+持久化）
    agent/                   # Agent核心模块（阶段36-85）
      __init__.py
      agent.py               # 智能体主体（初始化/执行/进化/自愈）
      eternal_loop.py        # 永续循环引擎（心跳/信号/资源熔断）
      startup.py             # 启动管理器（自检/种子注入/关闭）
      instance_lock.py       # 实例锁（多实例冲突检测）
    monitor/                 # 监控模块（阶段86-95）
      __init__.py
      metrics.py             # 指标采集器
      snapshot.py            # 系统状态快照
      execution_history.py   # 执行历史记录
      health_scorer.py       # 健康度评分器
      report_generator.py    # 运行报告生成器
  tests/                     # 测试套件（阶段1-100）
    __init__.py
    test_config.py           # 配置常量测试
    test_stage1_integration.py # 第一阶段集成测试
    test_kg.py               # 知识图谱模块测试
    test_task_queue.py       # 任务队列测试
    test_eternal_loop.py     # 永续循环引擎测试
    test_agent.py            # 智能体核心集成测试
    test_derive.py           # 知识推演测试
    test_evolution.py        # 知识进化测试
    test_startup.py          # 启动流程测试
    test_monitor.py          # 监控模块测试
    test_performance.py      # 性能基准测试（阶段96）
    test_stability.py        # 长时间稳定性测试（阶段97）
    test_edge_cases.py       # 边界条件与异常注入测试（阶段98）
  data/                      # 运行时数据（自动创建）
    knowledge_graph.json     # 知识图谱持久化
    task_queue.json          # 任务队列持久化
    system.log               # 系统日志
```

## 快速启动指南

```bash
# 克隆项目
cd eternal-agent

# 无需安装依赖（零外部依赖）
python main.py
# 输出: 永动知识图谱 Agent v1.0.0 启动中...

# 运行全部测试
python -m unittest discover -s tests -v

# 运行单个测试文件
python -m unittest tests.test_kg -v
python -m unittest tests.test_performance -v

# 停止系统: Ctrl+C (SIGINT) 或 kill (SIGTERM)
```

## 配置参数说明

所有配置集中在 `src/config.py`，每个参数都标注了公理溯源。

| 参数 | 默认值 | 说明 | 公理溯源 |
|------|--------|------|----------|
| `LOOP_DELAY` | 0.3 | 主循环迭代间隔(秒) | 存续公理 |
| `EVOLVE_STEP` | 50 | 触发知识进化的累计循环步数 | 自驱公理 |
| `KG_SAVE_PATH` | data/knowledge_graph.json | 知识图谱持久化路径 | 记忆公理 |
| `TASK_QUEUE_SAVE_PATH` | data/task_queue.json | 任务队列持久化路径 | 记忆公理 |
| `LOG_FILE_PATH` | data/system.log | 系统日志路径 | 存续公理 |
| `TASK_QUEUE_MAX` | 200 | 任务队列最大容量 | 自驱公理 |
| `SYSTEM_VERSION` | 1.0.0 | 系统版本号 | 存续公理 |

## API文档

### 核心类

#### KnowledgeGraph (`src/kg/knowledge_graph.py`)
知识图谱核心类，系统的唯一长期记忆载体。

| 方法 | 说明 |
|------|------|
| `add_node(name, attr)` | 添加节点（按名称去重） |
| `get_node(node_id)` | 根据ID获取节点 |
| `get_node_by_name(name)` | 根据名称获取节点 |
| `remove_node(node_id)` | 删除节点及其关联边 |
| `invalidate_node(node_id)` | 软删除（标记无效） |
| `add_edge(source, target, relation, weight)` | 添加边（自动创建节点，按三元组去重） |
| `get_edges_by_source/target/relation()` | 按条件查询边 |
| `remove_edge(source_id, target_id, relation)` | 删除指定边 |
| `save()` | 持久化到JSON文件 |
| `load()` | 从JSON文件恢复 |
| `get_stats()` | 获取统计信息 |
| `derive_new_tasks(node_name, threshold)` | 从指定节点推演新任务 |
| `derive_multi_hop_tasks(node_name, max_hops, threshold)` | 多跳关联推演 |
| `trim_invalid_knowledge(threshold)` | 修剪低权重边和孤立节点 |
| `decay_edges(factor)` | 衰减所有边权重 |
| `strengthen_edge(source, target, relation, boost)` | 增强指定边权重 |
| `normalize_weights()` | 归一化权重到[0,1] |
| `backup_graph(backup_dir, max_backups)` | 备份图谱文件 |

#### TaskQueue (`src/task/task_queue.py`)
有限长度任务队列，系统行为的唯一驱动源。

| 方法 | 说明 |
|------|------|
| `add_task(task)` | 入队（满队/重名返回False） |
| `batch_add_tasks(tasks)` | 批量入队 |
| `get_task()` | 出队（空返回None） |
| `peek()` | 查看队首但不弹出 |
| `is_empty()` / `is_full()` | 状态查询 |
| `save()` / `load()` | 持久化 |
| `clear()` | 清空队列 |

#### EternalSelfAgent (`src/agent/agent.py`)
永动自驱智能体，三大公理的交汇点。

| 方法 | 说明 |
|------|------|
| `__init__(base_dir)` | 初始化所有子系统 |
| `inject_initial_task()` | 注入初始任务 |
| `get_current_task()` | 获取下一个待执行任务 |
| `execute_task(task)` | 执行任务并沉淀知识 |
| `idle_self_evolve()` | 空闲时自主进化 |
| `health_check()` | 整合健康检查 |
| `self_repair()` | 异常自愈 |
| `eternal_loop()` | 永动主循环 |
| `run()` / `stop()` | 启动/停止 |

#### EternalLoop (`src/agent/eternal_loop.py`)
永续循环引擎，系统心跳节拍。

| 方法 | 说明 |
|------|------|
| `run()` | 启动循环（自动注册信号处理） |
| `self_repair()` | 自愈重启 |
| `health_check()` | 获取健康指标 |
| `resource_check()` | 内存资源熔断检查 |

#### TaskDeriver (`src/kg/task_deriver.py`)
知识推演器，自驱动力的核心引擎。

| 方法 | 说明 |
|------|------|
| `derive_from_task(task_name, threshold)` | 综合推演，返回Task列表 |

#### KnowledgeEvolution (`src/kg/evolution.py`)
知识进化器，编排完整的知识优化周期。

| 方法 | 说明 |
|------|------|
| `evolve(decay, trim, backup_dir, max_backups)` | 执行完整进化周期 |

#### 监控模块 (`src/monitor/`)

| 类 | 说明 |
|----|------|
| `MetricsCollector` | 指标采集（运行时长、循环次数、内存等） |
| `SystemSnapshot` | 系统状态快照生成与保存 |
| `ExecutionHistory` | 任务执行历史记录与查询 |
| `HealthScorer` | 综合健康度评分（0-100） |
| `ReportGenerator` | 运行报告生成与保存 |

## 100阶段实现里程碑

| 阶段 | 内容 | 模块 |
|------|------|------|
| 1-10 | 项目骨架、配置、日志、时钟、路径管理 | `config`, `logger`, `clock`, `path_manager` |
| 11-25 | Node/Edge数据结构、ID生成、图谱CRUD、持久化 | `kg/node`, `kg/edge`, `kg/id_generator`, `kg/knowledge_graph` |
| 26-35 | Task数据结构、有限长度任务队列 | `task/task`, `task/task_queue` |
| 36-45 | 永续循环引擎（心跳/异常/自愈/信号/资源熔断） | `agent/eternal_loop` |
| 46-55 | Agent主体（初始化/任务执行/知识沉淀/健康检查） | `agent/agent` |
| 56-65 | 知识推演器（单跳/多跳/频率控制/优先级映射） | `kg/task_deriver` |
| 66-75 | 知识进化器（衰减/修剪/归一化/备份） | `kg/evolution` |
| 76-85 | 启动管理（自检/实例锁/种子注入/优雅关闭） | `agent/startup`, `agent/instance_lock` |
| 86-90 | 监控模块（指标采集/快照/执行历史） | `monitor/metrics`, `monitor/snapshot`, `monitor/execution_history` |
| 91-95 | 监控完善（健康度评分/报告生成） | `monitor/health_scorer`, `monitor/report_generator` |
| 96 | 性能基准测试 | `tests/test_performance` |
| 97 | 长时间稳定性测试 | `tests/test_stability` |
| 98 | 边界条件与异常注入测试 | `tests/test_edge_cases` |
| 99 | 代码审查与重构 | 全部源文件 |
| 100 | 最终交付（README/全量测试/验证） | `README.md` |

## 设计公理溯源表

| 设计决策 | 公理溯源 | 实现位置 |
|----------|----------|----------|
| 主循环 while system_alive | 存续公理 | `agent/eternal_loop.py` |
| 知识图谱JSON持久化 | 记忆公理 | `kg/knowledge_graph.py` |
| 任务队列驱动行为 | 自驱公理 | `task/task_queue.py` |
| 日志双输出(控制台+文件) | 存续公理 | `logger.py` |
| 系统时钟运行时长统计 | 存续公理 | `clock.py` |
| 节点/边序列化反序列化 | 记忆公理 | `kg/node.py`, `kg/edge.py` |
| 唯一ID生成(时间戳+随机) | 记忆公理 | `kg/id_generator.py` |
| 按名称去重节点 | 记忆公理 | `kg/knowledge_graph.py` |
| 按三元组去重边 | 记忆公理 | `kg/knowledge_graph.py` |
| 软删除(invalidate) | 记忆公理 | `kg/knowledge_graph.py` |
| 任务执行沉淀知识节点 | 记忆公理+自驱公理 | `agent/agent.py` |
| 自主衍生下一迭代任务 | 自驱公理 | `agent/agent.py` |
| 知识推演生成新任务 | 自驱公理 | `kg/task_deriver.py` |
| 推演频率控制 | 自驱公理 | `kg/knowledge_graph.py` |
| 边权重衰减 | 自驱公理 | `kg/knowledge_graph.py` |
| 修剪低权重知识 | 自驱公理 | `kg/knowledge_graph.py` |
| 权重归一化 | 自驱公理 | `kg/knowledge_graph.py` |
| 图谱备份 | 自驱公理 | `kg/knowledge_graph.py` |
| 有限队列容量 | 存续公理+自驱公理 | `config.py`, `task/task_queue.py` |
| 异常捕获与自愈 | 存续公理 | `agent/eternal_loop.py`, `agent/agent.py` |
| SIGINT/SIGTERM信号处理 | 存续公理 | `agent/eternal_loop.py` |
| 资源熔断(内存监控) | 存续公理 | `agent/eternal_loop.py` |
| 文件锁多实例检测 | 存续公理 | `agent/instance_lock.py` |
| 启动自检 | 存续公理 | `agent/startup.py` |
| 种子知识注入 | 记忆公理 | `agent/startup.py` |
| 优雅关闭保存状态 | 记忆公理+存续公理 | `agent/startup.py` |
| 指标采集 | 存续公理 | `monitor/metrics.py` |
| 系统快照 | 记忆公理 | `monitor/snapshot.py` |
| 执行历史记录 | 记忆公理 | `monitor/execution_history.py` |
| 健康度评分 | 存续公理 | `monitor/health_scorer.py` |
| 运行报告生成 | 存续公理 | `monitor/report_generator.py` |
| 零外部依赖 | 存续公理 | 全局 |
| 公理溯源注释 | 设计原则 | 全部源文件 |

## 设计原则

- **零外部依赖**：仅使用Python标准库
- **公理溯源**：每个模块、每个常量都标注其公理来源
- **极致精简**：无冗余代码，每行都可被三大公理解释
- **可测试**：标准unittest框架，CI友好
- **可持久化**：所有核心状态均可JSON序列化
- **可恢复**：异常后自愈，重启后从文件恢复
