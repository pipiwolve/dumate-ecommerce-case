# DuMate 完整演示 Runbook

## 1. 演示目标

面向客户项目经理演示：DuMate 从 GitHub 读取本周研发事实，识别版本进度和发布风险，
调用企业知识与专家资源增强判断，并使用 DuMate 自身能力生成两份不同信息密度的 PPT。

技术负责人版保留代码、PR、Diff、Review 和 CI 证据；客户项目经理版聚焦里程碑、
业务影响、风险、责任人、下一步和需要客户确认的决策。

## 2. 演示前准备

### 2.1 添加 GitHub 官方 MCP

在 DuMate 中启用 GitHub 官方 MCP，并授权读取公开仓库：

```text
pipiwolve/dumate-ecommerce-case
```

至少需要仓库、Issue、Pull Request、Commit、Review、Actions/Checks 和 Release 的只读
能力。不同版本的 GitHub MCP 工具名可能不同，演示步骤按业务对象描述，不绑定具体
工具名。

### 2.2 添加 ShopFlow 知识专家 MCP

```json
{
  "mcpServers": {
    "shopflow-knowledge-experts": {
      "url": "https://www.demofun.online/mcp",
      "type": "streamableHttp",
      "headers": {}
    }
  }
}
```

连接成功后只应发现 3 个工具：

```text
knowledge_search
knowledge_get_document
expert_match
```

如果工具列表中仍出现 `delivery_*`，说明 Connector 仍在使用旧的工具缓存，应刷新或
重新连接 MCP。

### 2.3 确认时间口径

现场演示以演示当天所在周为时间窗，结论只以 GitHub 官方 MCP 返回的当前状态为准。
建议明确写出起止时间和 `Asia/Shanghai` 时区，避免“本周”在不同系统中产生歧义。

## 3. 主演示流程：实时 GitHub + DuMate 原生 PPT

### 步骤 1：让 DuMate 建立计划基线

向 DuMate 输入：

```text
请审查 GitHub 仓库 pipiwolve/dumate-ecommerce-case 本周的研发交付情况。
先找到 v2.6 限时促销稳定性 Milestone 及其关联 Issue，把 Issue 当作计划基线。
保留所有证据 URL、Issue/PR 编号和 Commit SHA。暂时不要生成报告。
```

DuMate 应通过 GitHub 官方 MCP 获取 Milestone、关联 Issue、状态、标签、负责人和评论。

### 步骤 2：补齐代码与交付证据

继续输入：

```text
继续读取本周关联和未关联的 PR、Commit、changed files、Review、Check Run 与 Release。
对每个 Issue 给出完成证据；识别没有关联 Issue 的代码变化。不要用 Commit 数量或代码
行数计算业务进度。把结果整理成“事实证据表”。
```

演示仓库中可讲解的证据包括：

- BUG-102 首次修复失败，随后 PR #13 完成 Review Thread、CI、Approve 和 Merge。
- PERF-104 的批量库存查询修改完成评审和合并。
- PR #14 起初未关联 Issue，体现计划外缓存配置变更。
- HOTFIX-107 / PR #17 对风险缓存配置执行精确 Revert。
- `v2.6.0-rc.1` 与 `v2.6.0-rc.2` 展示发布候选状态演进。

### 步骤 3：形成风险清单

```text
基于事实证据表，按 inventory、performance、security、release 四类整理风险。
每条必须区分：已确认事实、基于事实的推断、仍需负责人确认的问题。列出受影响模块。
```

预期受影响模块包括库存预占、订单、购物车、后台管理、运行配置和质量门禁。

### 步骤 4：调用知识库增强判断

要求 DuMate 对每个高风险项执行：

```text
先调用 knowledge_search 查找相关企业规范或发布 SOP，再对最相关结果调用
knowledge_get_document。报告中保留文档标题、版本和来源；不要把模型常识写成企业规范。
```

示例：

- 库存并发：`inventory concurrency oversell atomicity`
- 购物车性能：`cart inventory performance n+1 batch`
- 管理端安全：`admin security rbac audit inventory`
- 发布门禁：`release quality-gate blocker customer`

### 步骤 5：匹配领域专家

```text
对每个高风险项调用 expert_match，输入风险标签和受影响模块。只推荐工具返回的专家，
保留匹配原因、当前可用状态和升级条件。明确这些人员是案例中的模拟专家。
```

BUG-102 应高置信匹配库存一致性专家；性能、安全和发布问题分别匹配对应领域人员。

### 步骤 6：先生成统一报告上下文

```text
把 GitHub 实时事实、知识证据和专家匹配整理为一个统一报告上下文。包含：统计时间窗、
仓库与 Milestone、完成事项、进行中事项、阻塞和风险、计划外变化、发布状态、证据链接、
知识来源、专家建议、待确认问题。为这份上下文生成唯一 report_context_id。两份 PPT 必须
使用完全相同的上下文，不得分别重新查询数据。
```

这是避免两份 PPT 口径不一致的关键控制点。

### 步骤 7：使用 DuMate 能力生成技术负责人版 PPT

```text
请基于统一报告上下文生成“技术负责人版”PPT。必须包含：
1. 本周版本结论与发布状态；
2. Issue/PR/Commit/Review/CI 证据链；
3. changed files、受影响模块和 Diff 风险；
4. 失败检查与修复闭环；
5. 知识依据与专家匹配；
6. 按负责人和时限排列的工程行动；
7. 附录中的证据 URL 和 SHA。
不要省略 report_context_id 和统计时间窗。
```

### 步骤 8：使用同一上下文生成客户项目经理版 PPT

```text
请使用完全相同的 report_context_id 生成“客户项目经理版”PPT。只保留：里程碑进度、
已完成业务结果、未完成范围、发布风险及客户影响、恢复动作、负责人、时间计划、需要客户
确认的决策。删除代码 Diff、内部事故细节、原始错误和未经确认的责任判断。
```

### 步骤 9：执行一致性检查

```text
比较两份 PPT：统计窗口、完成事项、风险数量、发布结论和下一步必须一致。技术版可以
包含更多证据，但不能出现与客户版相反的状态。列出检查结果后再交付文件。
```

### 步骤 10：模拟推送与审核

Demo 可以直接下载两份 PPT。正式上线时：

```text
技术负责人版 -> 内部自动推送
客户项目经理版 -> 内部项目经理审核 -> 批准后外发
```

无人审核或证据不完整时，客户版保持草稿，不自动发送。

## 4. 一次性演示提示词

以下提示词可在两个 MCP 均连接后直接使用：

```text
你是 ShopFlow v2.6 的交付审查 Agent。请使用 GitHub 官方 MCP 审查公开仓库
pipiwolve/dumate-ecommerce-case 本周的 Milestone、Issue、PR、Commit、changed files、
Review、Check Run 和 Release。以 Issue 为计划基线，不用 Commit 或代码行数代表进度；
识别没有关联 Issue 的变化，并保留证据 URL、编号和 SHA。

对重要风险调用 ShopFlow MCP 的 knowledge_search 和 knowledge_get_document，随后调用
expert_match。严格区分事实、推断和待确认项。先形成一个带 report_context_id 的统一上下文，
再使用 DuMate 自身的 PPT 生成能力输出两份文件：技术负责人版保留代码活动、模块、Diff、
CI、Review、知识和专家证据；客户项目经理版只保留进度、业务影响、风险、恢复动作、责任人
和待决策项。两份文件必须使用相同时间窗和上下文。PPT、审批和推送都由 DuMate 完成。
```

## 5. 每周五定时任务

建议在 DuMate 创建每周五 `17:00 Asia/Shanghai` 运行的任务，时间可以按项目例会调整。
统计窗口固定为本周一 `00:00` 到任务实际开始时间。

任务动作：

1. 通过 GitHub 官方 MCP 获取时间窗内更新的 Issue、PR、Commit、Diff、Review、Checks
   和 Release，并读取相关 Milestone 当前状态。
2. 形成事实证据表，识别完成事项、阻塞、计划外变化和证据缺口。
3. 对高风险项调用知识库和专家工具。
4. 生成唯一 `report_context_id`，由同一上下文生成两份 PPT。
5. Demo 直接推送两份文件；正式上线时技术版可自动推送，客户项目经理版进入人工审核。
6. 记录任务运行时间、GitHub 查询窗口、报告 ID、推送状态和失败原因。

任务必须使用幂等键，例如：

```text
pipiwolve/dumate-ecommerce-case + 2026-W32 + weekly-delivery
```

同一周重跑应更新同一任务记录，不能重复推送。GitHub、知识库或 PPT 任一步失败时，不应
发送内容不完整的客户报告；保留内部失败通知并允许人工重试。

## 6. 验收清单

- GitHub 官方 MCP 能读取目标仓库并返回指定时间窗的实时数据。
- ShopFlow MCP 只发现 3 个工具，并成功调用知识检索、正文读取和专家匹配。
- 本周代码活动都能关联 Issue；未关联变化被单独标记。
- 结论区分事实、推断和待确认项。
- 两份 PPT 共用一个 `report_context_id` 和统计时间窗。
- 技术版包含代码级证据，客户版完成脱敏且保留业务影响。
- PPT、定时任务、审批和推送均由 DuMate 执行。
- 正式外发路径包含人工审核，不由 Demo 推送预览代替。
