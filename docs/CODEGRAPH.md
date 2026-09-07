# 维知 Agent — 架构与调用链

> 本文描述当前代码结构。产品名为“维知 Agent（Weizhi Agent）”；代码中的 `TongYong` 类名和 `tongyong` 包标识为兼容性名称。

## 系统边界

```text
Browser / OpenAI-compatible client / IM
                  │
                  ▼
             FastAPI routes
                  │
        ┌─────────┴─────────┐
        ▼                   ▼
 Single Agent          Multi-Agent Team
 LangGraph ReAct       Scheduler + EventBus
        │                   │
        └─────────┬─────────┘
                  ▼
          LLM adapters + tools
                  │
       SQLite / ChromaDB / files
```

## 后端模块

| 模块 | 职责 |
|---|---|
| `app/main.py` | 创建 FastAPI 应用、注册中间件和路由 |
| `app/lifespan.py` | 初始化工具、MCP、LLM 验证与后台服务 |
| `app/startup.py` | 构造 `AgentEngine` 并注入当前 LLM |
| `app/api/` | 聊天、流式、记忆、模型、技能、文件、追踪等 REST API |
| `app/core/agent.py` | 单 Agent 核心与自研 ReAct 回退循环 |
| `app/core/langchain_agent.py` | 默认 LangGraph ReAct 流程 |
| `app/core/runtime/` | 计划、反思、IPC 和 trace |
| `app/core/multi_agent/` | 团队、角色、事件总线、调度器与任务队列 |
| `app/llm/` | 多供应商模型适配与 OpenAI 兼容适配器 |
| `app/tools/` | 工具注册、执行、权限、审批、审计和 MCP 客户端 |
| `app/memory/` | SQLite 会话/记忆和 ChromaDB 向量检索 |
| `app/skills/` | Skill 扫描、管理和加载 |
| `app/dreaming/` | Light → REM → Deep 三阶段记忆整理 |
| `app/gateway/` | OpenAI 兼容接口、IM 网关和桌面桥接 |
| `app/hermes/` | 平文件记忆、技能文件、约束与提示机制 |

## 前端模块

| 模块 | 职责 |
|---|---|
| `src/App.tsx` | 页面框架、会话导航和主要视图切换 |
| `components/Chat/` | 流式聊天、Markdown、计划卡片和文件预览 |
| `hooks/useStreamChat.ts` | SSE 流状态机 |
| `components/Team/` | 多智能体团队配置与运行 |
| `components/Settings/` | 模型、记忆、技能、梦境和评估设置 |
| `components/Skills/` | Skill 与 MCP 市场 |
| `src/api/` | 前端 API 客户端 |

## 单 Agent 流式链路

```text
ModernChatPanel
  → streamChat()
  → POST /api/chat/stream
  → generate_stream_response()
  → stream_chat_langchain()              默认
  → TongYongLLMAdapter
  → create_react_agent()
  → ToolRegistry / MCP client
  → content、thinking、tool、usage、done 等 SSE 事件
```

`LANGCHAIN_ROLLOUT` 控制默认路径比例：`100` 为全量 LangGraph，`0` 为全部回退到 `AgentEngine.stream_chat()`。

## 多 Agent 链路

```text
TeamPanel
  → /api/team/sessions/{id}/run
  → Team.run_v2_stream()
  → Scheduler
  → EventBusEnvironment + TaskQueue
  → TeamRole
  → LLM + ToolManager
```

团队支持：

- `pipeline`：按角色连接图分发和验收任务。
- `debate`：多个立场角色依序发言，再由裁判角色汇总。

旧 `run_stream()` 仍用于兼容；新功能应基于 `run_v2_stream()`。

## 数据与状态

- `backend/data/agent.db`：会话、消息、记忆和设置。
- `backend/data/chroma/`：可选向量索引。
- LangGraph checkpoint：保存可继续执行的图状态。
- runtime trace：记录模型调用、工具跨度和交付结果。
- Team SQLite：保存团队会话、事件与任务状态。

数据根目录由 `TONGYONG_DATA_DIR` 覆盖，默认是 `backend/data/`。

## 扩展点

- 新模型：实现 `BaseLLM` 或复用 `OpenAICompatibleLLM`，并在 factory/catalog 注册。
- 新工具：在 `app/tools/implementations/` 中实现并通过 `_register_tools()` 显式注册。
- 新 Skill：提供带元数据的技能目录，通过 Skill 管理器安装和加载。
- 新 MCP：通过配置注册 stdio 或远程 MCP Server。
- 新团队策略：扩展 multi-agent action、角色模板或 Scheduler 行为。

## 当前注意事项

- 默认模型是 `edgefn / GLM-4.5V`，但凭据必须由 `EDGEFN_API_KEY` 提供。
- 业务管理 API 尚无统一认证层；公网部署必须增加反向代理认证或应用级鉴权。
- 终端、桌面和文件写入工具具有高影响能力，生产环境应启用审批和隔离。
- `vision/` 与部分 `scheduler/` 目录仍是预留边界，不代表完整功能。

带日期的代码审查和 `historical-reviews/` 反映当时版本，不应覆盖本文的当前架构描述。
