# 维知 Agent 能力说明

> 本文描述当前实现，不再使用早期已移除的 `/api/intelligent/*` 接口。

## 对话与执行

Agent 可以进行普通问答，也可以进入 ReAct 循环完成多步骤任务：理解需求、选择工具、执行、读取结果、修正并交付。默认流式入口是 `POST /api/chat/stream`。

## 内置工具类别

| 类别 | 代表工具 | 作用 |
|---|---|---|
| 文件 | `read_file`、`write_file`、`patch`、`search_files`、`glob`、`grep`、`ls` | 阅读、搜索和修改项目文件 |
| 工作区 | `workspace_info`、`workspace_list`、`workspace_read`、`workspace_write`、`workspace_terminal` | 在会话隔离工作区完成任务 |
| 命令 | `terminal`、`install_dependencies` | 执行命令和安装依赖 |
| 网页 | `web_search`、`web_extract`、`browser`、`playwright` | 搜索、读取和操作网页 |
| 记忆 | `memory_search`、`memory_list` | 显式检索会话或长期记忆 |
| 附件 | `attachment_list`、`attachment_read` | 读取本轮上传的文件 |
| 计划 | `todo_write`、`todo_read` | 维护长任务清单和进度 |
| Skill | `skill_list`、`skill_view`、`load_skill`、`skill_install` | 查找、加载与安装技能 |
| 自建 Skill | `self_skill_draft`、`self_skill_validate`、`self_skill_install` | 创建并验证可复用技能 |
| 协作 | `delegate_task` | 将子任务委派给子 Agent |
| 设备 | `desktop`、`adb`、`cdp` | 桌面、Android 和浏览器调试能力 |
| 人机协作 | `ask` | 在信息不足时向用户提问 |

工具是否可用取决于运行环境、权限策略、依赖和模型是否支持工具调用。

## 计划模式

前端可以先调用 `/api/plan/build` 生成结构化步骤，在用户批准后把计划加入对话上下文，再走正常的流式执行链。长任务达到单轮预算后可以通过 `continue_prompt` 续跑。

## 记忆能力

- SQLite 保存会话、消息、记忆、设置与版本。
- ChromaDB 可用于语义检索；缺少依赖时会降级为关闭状态。
- 跨会话内容不会自动混入新会话，必须通过记忆工具显式检索。
- 上下文接近模型窗口阈值时可以进行摘要压缩。
- Dreaming 子系统可按 Light、REM、Deep 三阶段筛选和巩固候选记忆，默认关闭。

## 多智能体能力

- Pipeline：Leader、Coder、Tester、Reviewer 等角色按连接图协作。
- Debate：多个立场角色轮流发言，由裁判角色汇总。
- v2 调度器通过 SQLite 事件总线与任务队列管理任务认领、完成、失败和超时。

## 扩展能力

- LLM：支持内置供应商和 OpenAI 兼容供应商。
- Skill：可上传本地技能，也可从 Marketplace/Community Hub 安装。
- MCP：可以安装并连接 stdio 或远程 MCP Server，将其工具加入注册表。
- Gateway：可通过 `/v1/chat/completions` 为第三方客户端提供 OpenAI 兼容访问。

## 安全与交付约束

- 高风险命令进入审批队列，批准信息必须与待执行命令匹配。
- 工具具有权限与审计层，运行环境还可以附加沙盒策略。
- 写文件、构建等任务需要真实工具证据；缺少证据时不能仅凭模型文本标记完成。
- API Key 只应放在环境变量或本地配置中，不应写进源码。
