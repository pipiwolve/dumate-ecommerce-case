# DuMate 接入说明

## 本地知识与专家 MCP

启动：

```bash
MCP_TRANSPORT=streamable-http uv run python -m shopflow.mcp_server
```

DuMate 导入：

```json
{
  "mcpServers": {
    "shopflow-delivery-knowledge": {
      "url": "http://127.0.0.1:8130/mcp",
      "type": "streamableHttp",
      "headers": {}
    }
  }
}
```

推荐先调用 `delivery_build_snapshot`，再调用 `knowledge_search`、`expert_match` 和
`delivery_generate_reports`。详细编排规则见仓库内 Skill。

## GitHub 官方 MCP

本地 JSON 仅用于离线验收和发布种子。将仓库发布至 GitHub 后，把
`scenario/github/seed.json` 中的 `OWNER/ecommerce-delivery-case` 替换为实际仓库，
再通过 DuMate 官方 GitHub MCP 读取 Milestone、Issue、PR 和 Commit。

线上写入脚本默认 dry-run，只有同时提供 `--repo` 和 `--apply` 才会调用 `gh`。
运行前先确认目标账号、仓库可见性和 GitHub 登录状态。

Dry-run 示例：

```bash
uv run python scripts/github_seed.py --repo OWNER/ecommerce-delivery-case
```

确认输出后才使用 `--apply`。脚本会创建一期 Milestone 与 Issue，并为 BUG-102 和
PERF-104 创建开放 PR；已进入 `main` 的 FEAT-101 与 BUG-103 以关闭 Issue 和真实
Commit 作为完成证据。
