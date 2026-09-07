# AGENTS.md — 维知 Agent 协作上下文

> 当前事实来源。产品名统一为“维知 Agent（Weizhi Agent）”；Python 包名、仓库内部标识和环境变量保留 `tongyong`，避免破坏兼容性。

## 项目概览

维知 Agent 是 FastAPI + React 构建的通用智能体平台。它支持多模型、LangGraph ReAct 工具执行、持久化记忆、Skill/MCP 扩展、多智能体协作和 OpenAI 兼容网关。

当前代码快照：

| 项目 | 当前值 |
|---|---|
| 后端源码 | 约 214 个 Python 文件 |
| 前端源码 | 约 72 个 TS/TSX/JSX 文件 |
| HTTP 路由 | 约 263 个路由声明 |
| 后端端口 | `8000` |
| 前端开发端口 | `5173` |
| 默认执行路径 | LangGraph ReAct，`LANGCHAIN_ROLLOUT=100` |
| 默认模型配置 | `edgefn / GLM-4.5V`，必须通过 `EDGEFN_API_KEY` 提供凭据 |
| 持久化 | SQLite + 可选 ChromaDB |

数量是当前工作树快照，新增文件和路由后会自然变化。

## 关键入口

```text
backend/app/main.py                    FastAPI 装配与路由注册
backend/app/lifespan.py                启动和关闭生命周期
backend/app/startup.py                 AgentEngine 与 LLM 初始化
backend/app/api/stream.py              SSE 对话入口与执行路径选择
backend/app/core/langchain_agent.py    默认 LangGraph ReAct 路径
backend/app/core/agent.py              AgentEngine 与自研回退循环
backend/app/core/multi_agent/          多智能体编排、事件总线和任务队列
backend/app/tools/                     内置工具、权限、审批、审计与 MCP
backend/app/memory/                    SQLite 会话记忆与 ChromaDB 向量检索
backend/app/gateway/                   OpenAI 兼容、IM 与桌面桥接网关
frontend/src/App.tsx                   Web UI 总入口
frontend/src/hooks/useStreamChat.ts    前端流式状态机
```

## 主要调用链

单智能体流式对话：

```text
ModernChatPanel
  → POST /api/chat/stream
  → api/stream.py
  → stream_chat_langchain()
  → TongYongLLMAdapter
  → LangGraph ReAct
  → ToolRegistry / MCP
  → SSE 事件返回前端
```

多智能体协作：

```text
TeamPanel
  → /api/team/sessions/{id}/run
  → Team.run_v2_stream()
  → Scheduler + EventBusEnvironment
  → AgentTask / TaskQueue
  → LLM + ToolManager
```

## 开发与验证

后端依赖以 `backend/requirements.txt` 为准；根目录 `pyproject.toml` 仅用于可选的本地视觉依赖。

```bash
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

```bash
cd frontend
npm ci
npm run dev
npm run build
```

后端测试位于 `backend/tests/`。运行测试时应使用独立的 `TONGYONG_DATA_DIR`，避免污染本地运行数据；需要跳过启动时模型验证时设置 `SKIP_LLM_VALIDATION=1`。

## 数据与安全边界

- 运行时数据统一由 `backend/app/paths.py` 定位，默认目录是 `backend/data/`。
- `.env`、`backend/data/`、虚拟环境、本机工具配置和缓存不得提交。
- 所有模型凭据必须来自环境变量或本地配置；源码不得包含可用密钥。
- 文件、终端和桌面工具属于高影响能力，改动权限或审批逻辑时必须补测试。
- 不要清理 `backend/data/`，除非用户明确要求删除运行数据。

## 文档约定

- `README.md`：用户入口、安装和运行方法。
- `docs/CODEGRAPH.md`：当前架构与调用链。
- `docs/API.md`：当前 API 分组和入口。
- `docs/AGENT_CAPABILITIES.md`：当前 Agent 能力。
- 带日期的审查、`docs/historical-reviews/`、增强方案和转型方案是历史资料，不作为当前实现依据。

更新架构、默认配置或运行方式时，应同步修改上述当前文档。历史资料只增加状态说明，不回写成当前事实。
