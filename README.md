# ShopFlow 电商版本交付案例

这是一个可重复运行的本地 Git 项目，用于在 DuMate 中演示：

- 通过 GitHub 官方 MCP 跟进 Milestone、Issue、PR、Review 和 Check Run。
- 通过真实 Git Commit 与 Diff 判断受影响模块和计划外变更。
- 通过自建 MCP 检索固定领域知识并匹配企业专家。
- 由 DuMate 从同一报告上下文生成技术负责人版与客户项目经理版 PPT。

真实 GitHub 仓库：<https://github.com/pipiwolve/dumate-ecommerce-case>

## 业务场景

ShopFlow v2.6 在限时促销前新增库存预占与超时释放能力。仓库保留了 2026-08-06 的
历史风险案例及后续修复链路；DuMate 运行时结论始终以 GitHub 官方 MCP 的实时状态为准。

## 本地运行

```bash
uv sync --extra dev
uv run pytest
uv run uvicorn shopflow.api:app --app-dir src --port 8140
```

知识与专家 MCP：

```bash
MCP_TRANSPORT=streamable-http uv run python -m shopflow.mcp_server
```

默认 HTTP 地址为 `http://127.0.0.1:8130/mcp`。完整场景说明、GitHub 发布步骤和
DuMate 工具调用顺序见 `docs/CASE.md` 与 `skills/ecommerce-delivery-review/SKILL.md`。
联网演练产生的真实对象与覆盖矩阵见 `docs/GITHUB_FLOW_EVIDENCE.md`。

自建 MCP 的 3 个工具、数据来源和公网行为见 `docs/MCP_TOOL_REFERENCE.md`。使用 GitHub
官方 MCP 获取实时研发事实、调用知识专家增强并由 DuMate 原生生成双角色 PPT 的完整
演示步骤见 `docs/DUMATE_DEMO_RUNBOOK.md`。

公网演示使用 Vercel ASGI 入口 `api/index.py`，只发布无状态 `/mcp` 网关供 DuMate
Connector 完成协议验证和工具调用。公网连接配置与只读安全边界见
`docs/DUMATE_CONNECT.md`。

GitHub 上的 Milestone、Issue、PR、Review、Check Run、Release 与 Hotfix 是联网
演示的事实来源；`scenario/github/seed.json` 仅保留可重复初始化与离线测试数据。
知识库与专家目录的覆盖范围和权限边界见 `docs/KNOWLEDGE_EXPERT_SCOPE.md`。

## 边界

仓库内的 GitHub JSON 是可重复的发布种子和离线验收数据。生产/联网演示时，
Issue、PR、Review 与 Check Run 应由 DuMate 官方 GitHub MCP 读取，本项目不复制
GitHub MCP 的职责。
