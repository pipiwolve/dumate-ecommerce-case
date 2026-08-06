# ShopFlow 电商版本交付案例

这是一个可重复运行的本地 Git 项目，用于在 DuMate 中演示：

- 通过 GitHub 官方 MCP 跟进 Milestone、Issue、PR、Review 和 Check Run。
- 通过真实 Git Commit 与 Diff 判断受影响模块和计划外变更。
- 通过自建 MCP 检索领域知识、匹配专家并冻结统一证据快照。
- 从同一快照生成技术负责人版与客户项目经理版 PPT。

## 业务场景

ShopFlow v2.6 在限时促销前新增库存预占与超时释放能力。本期快照冻结于
2026-08-06 18:00（Asia/Shanghai），功能已部分合并，但并发超卖仍阻塞发布。

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

## 边界

仓库内的 GitHub JSON 是可重复的发布种子和离线验收数据。生产/联网演示时，
Issue、PR、Review 与 Check Run 应由 DuMate 官方 GitHub MCP 读取，本项目不复制
GitHub MCP 的职责。

