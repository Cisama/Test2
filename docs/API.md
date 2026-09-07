# 维知 Agent API 速查

> 当前服务以 FastAPI 自动生成的 OpenAPI 文档为最终接口事实来源。调试模式下启动后访问 `http://localhost:8000/docs`。

## 基础信息

- 默认地址：`http://localhost:8000`
- 普通接口：JSON
- 流式对话：Server-Sent Events（SSE）
- OpenAI 兼容入口：`/v1`
- 当前业务管理接口未统一启用身份认证；OpenAI 兼容网关使用独立网关认证配置。

## 核心接口

| 方法 | 路径 | 用途 |
|---|---|---|
| `GET` | `/`、`/health`、`/ready` | 服务状态与就绪检查 |
| `POST` | `/api/chat` | 非流式单 Agent 对话 |
| `POST` | `/api/chat/stream` | SSE 流式对话 |
| `POST` | `/api/chat/clarify` | 回答 Agent 的澄清问题 |
| `POST` | `/api/chat/compress` | 主动压缩会话上下文 |
| `GET` | `/api/chat/context-stats/{session_id}` | 查看上下文容量 |
| `POST` | `/api/plan/build` | 为任务生成执行计划 |
| `POST` | `/v1/chat/completions` | OpenAI Chat Completions 兼容接口 |

## 会话与记忆

| 前缀 | 用途 |
|---|---|
| `/api/memory/sessions` | 会话列表 |
| `/api/memory/create` | 创建会话 |
| `/api/memory/messages/{session_id}` | 读取会话消息 |
| `/api/memory/session/{session_id}` | 更新或删除会话 |
| `/api/memory/search` | 搜索长期记忆 |
| `/api/memory/settings` | 会话记忆设置 |

## 模型与网关

| 前缀 | 用途 |
|---|---|
| `/api/llm` | 供应商、模型、连接测试和运行时切换 |
| `/api/gateway/profiles` | 网关 Profile 管理 |
| `/api/gateway/gateways` | Profile 网关进程状态与启停 |
| `/api/im` | IM 网关状态 |
| `/v1` | OpenAI 兼容 API |

## 工具、文件与附件

| 前缀 | 用途 |
|---|---|
| `/api/tools` | 工具列表、执行、提问和审批 |
| `/api/files` | 本地交付文件的信息、预览和读取 |
| `/api/chat/attachments` | 会话附件上传和访问 |
| `/api/trace` | Runtime trace 查询 |

高风险终端操作需要通过 `/api/tools/approvals` 审批闭环。文件接口只处理允许范围内的本地路径，不接受远程 URL 作为本地文件。

## Skill 与 MCP

| 前缀 | 用途 |
|---|---|
| `/api/skills` | 已安装 Skill 的查询、上传、分类与触发匹配 |
| `/api/marketplace` | Skill 市场与安装 |
| `/api/hub` | Community Hub 搜索、来源与同步 |
| `/api/mcp` | MCP 市场、Server 安装、删除和重启 |
| `/api/skills/coze` | Coze Skill 市场适配 |
| `/api/hermes` | Hermes 平文件记忆和 Skill 管理 |

## 多智能体

多智能体接口统一位于 `/api/team`：

- `/sessions`：团队会话管理。
- `/sessions/{id}/roles`：角色管理。
- `/sessions/{id}/connections`：角色连接关系。
- `/sessions/{id}/run` 与 `/run/stream`：启动团队任务并读取事件。
- `/sessions/{id}/tasks`：v2 任务创建、拆解、认领、完成和拒绝。
- `/sessions/{id}/scheduler`：调度器状态与停止。
- `/marketplace`：Agent 模板市场。

## 其他子系统

| 前缀 | 用途 |
|---|---|
| `/api/dreaming` | 三阶段记忆整理、配置、候选与日志 |
| `/api/evaluation` | 任务评估、指标与历史结果 |
| `/api/voice` | 语音转写、语音合成与音频访问 |
| `/api/chart` | 图表 API 占位入口，尚未接入生成逻辑 |
| `/api/contact` | 联系表单 |

## 流式事件

`POST /api/chat/stream` 会按执行进度产生事件，常见类型包括：

- `start`、`progress`
- `thinking_delta`、`thinking_done`
- `content`
- `tool_start`、`tool_complete`、`tool_error`
- `context`、`usage`、`budget_warning`
- `done`、`error`

`done` 可能携带 `needs_continue`、`stop_reason` 与 `continue_prompt`，供长任务在达到单轮上限后继续执行。

## 示例

```bash
curl -N http://localhost:8000/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message":"分析当前目录并给出摘要","session_id":"demo"}'
```

接口请求体会随功能演进；编写客户端前应查看运行实例的 `/docs` 或 `/openapi.json`，不要只依赖本文示例。
