# 维知 Agent

> 英文名：Weizhi Agent；代码包与环境变量继续使用历史标识 `tongyong` / `TONGYONG_*`，以保持兼容。

维知 Agent 是一个面向真实任务的通用 AI 智能体平台。它通过 Web 界面或 OpenAI 兼容 API 接收任务，由大模型规划并调用文件、终端、网页、记忆、附件和技能工具完成工作，同时保留会话、执行轨迹与交付证据。

## 核心能力

- 多模型：支持 OpenAI、通义千问、DeepSeek、Anthropic、MiniMax、Gemini、Ollama 及 OpenAI 兼容服务。
- 智能体执行：默认使用 LangGraph ReAct，也保留自研执行循环作为回退路径。
- 工具系统：支持文件读写、终端、网页、附件、记忆、待办、工作区、技能和 MCP 工具。
- 记忆与上下文：SQLite 保存会话与消息，ChromaDB 提供可选语义检索，并支持上下文压缩。
- 多智能体：支持流水线与辩论模式，可配置角色、连接关系和任务队列。
- 扩展能力：支持本地 Skill、技能市场、MCP Server 和自建技能。
- 可观测性：通过 SSE 返回思考、工具调用、用量和完成状态，并记录 runtime trace。
- Web UI：提供流式聊天、计划模式、附件、团队协作、模型配置、记忆与技能管理。

## 技术栈

- 后端：Python 3.11、FastAPI、LangChain、LangGraph、SQLite、ChromaDB
- 前端：React 18、TypeScript、Vite 6
- 运行方式：本地开发或 Docker
- 默认端口：后端 `8000`，前端开发服务器 `5173`

## 快速开始

### 1. 配置模型

复制环境变量示例，并至少配置一个模型供应商的 API Key。默认供应商是 EdgeFn，默认模型是 `GLM-4.5V`：

```bash
cp backend/.env.example backend/.env
```

在 `backend/.env` 中设置：

```dotenv
EDGEFN_API_KEY=your-api-key
```

也可以改用其他供应商，并通过 Web 设置页或相应环境变量选择模型。源码不包含可用 API Key。

### 2. 本地开发

后端依赖的单一事实源是 `backend/requirements.txt`：

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

另开终端启动前端：

```bash
cd frontend
npm ci
npm run dev
```

打开 `http://localhost:5173`。后端调试模式下的 API 文档位于 `http://localhost:8000/docs`。

### 3. Docker

当前 Dockerfile 使用预构建的前端资源，因此先构建前端，并在仓库根目录准备 Docker Compose 使用的 `.env`：

```bash
cd frontend
npm ci
npm run build
cd ..
cp .env.example .env
# 编辑 .env，填入 EDGEFN_API_KEY 或其他供应商凭据
docker compose up --build -d
```

容器当前暴露后端 API；使用 `http://localhost:8000/health` 检查状态。Web UI 开发模式仍通过 `frontend` 目录下的 `npm run dev` 启动。

## 主要目录

```text
.
├── backend/app/       # FastAPI、Agent、LLM、工具、记忆与网关
├── frontend/src/      # React Web UI
├── mcp_servers/       # 内置 MCP Server 示例
├── docs/              # 当前架构、API 与专题文档
├── notes/             # 开发记录
├── Dockerfile
└── docker-compose.yml
```

运行时数据默认写入 `backend/data/`，也可以通过 `TONGYONG_DATA_DIR` 改写。该目录不会提交到 Git。

## 文档

- [架构与调用链](docs/CODEGRAPH.md)
- [API 入口速查](docs/API.md)
- [Agent 能力说明](docs/AGENT_CAPABILITIES.md)
- [Agent 协作说明](AGENTS.md)

带日期的代码审查、`historical-reviews/` 和标注为“历史方案”的文档仅用于追溯，不代表当前实现。

## 安全提示

- 不要提交 `.env`、本地数据库、模型密钥或第三方凭据。
- `terminal` 与 `workspace_terminal` 可以执行系统命令；生产部署应启用权限、审批与隔离策略。
- 当前业务管理 API 未统一启用身份认证，不应直接暴露在公网。
