# DuMate 接入说明

## 公网 DuMate Connector MCP

Vercel 部署后，DuMate 使用 Streamable HTTP 连接：

```json
{
  "mcpServers": {
    "shopflow-delivery-knowledge": {
      "url": "https://www.demofun.online/mcp",
      "type": "streamableHttp",
      "headers": {}
    }
  }
}
```

Vercel 只发布 `/mcp`，它是供 DuMate Connector 完成 `initialize`、`tools/list` 和
工具调用的无状态 MCP 网关，不依赖展示网站。Vercel 的函数重写路径会在 ASGI 层
归一化为 `/mcp`，实现方式与现有 CRM MCP 服务一致。

公网环境为只读演示模式：`delivery_build_snapshot` 不写文件，报告工具返回仓库中
预生成的两份 PPT 制品，`delivery_simulate_push` 只返回推送预览而不发送外部消息。
默认权限主体为 `principal_delivery`，不会公开 restricted 事故复盘正文。正式业务上线前
需要增加组织身份认证、知识库 ACL 映射、调用审计和报告人工审核。

如设置 `MCP_AUTH_TOKEN`，DuMate Connector 需要传入
`Authorization: Bearer <token>`；当前无 Token 配置适用于合成数据联调。接口中的项目、
人员和知识内容均为模拟数据。

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

固定案例可先调用 `delivery_build_snapshot`，再调用 `knowledge_search`、
`expert_match`。实时演示应以 GitHub 官方 MCP 为事实来源，并使用 DuMate 自身能力生成
PPT；`delivery_generate_reports` 在公网只返回预生成案例制品。工具契约见
`MCP_TOOL_REFERENCE.md`，完整步骤见 `DUMATE_DEMO_RUNBOOK.md`。

## GitHub 官方 MCP

本地 JSON 仅用于离线验收和发布种子。真实演示仓库为
`pipiwolve/dumate-ecommerce-case`，DuMate 官方 GitHub MCP 读取该仓库的
Milestone、Issue、PR、Review、Check Run、Commit 和 Release。

线上写入脚本默认 dry-run，只有同时提供 `--repo` 和 `--apply` 才会调用 `gh`。
运行前先确认目标账号、仓库可见性和 GitHub 登录状态。

Dry-run 示例：

```bash
uv run python scripts/github_seed.py --repo pipiwolve/dumate-ecommerce-case
```

确认输出后才使用 `--apply`。脚本会创建一期 Milestone 与 Issue，并为 BUG-102 和
PERF-104 创建开放 PR；已进入 `main` 的 FEAT-101 与 BUG-103 以关闭 Issue 和真实
Commit 作为完成证据。
