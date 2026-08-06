# 真实 GitHub 完整开发流证据

仓库：<https://github.com/pipiwolve/dumate-ecommerce-case>

## 覆盖矩阵

| 流程 | 真实证据 | 结果 |
|---|---|---|
| Repository 与 Git 历史 | Public 仓库、4 条开发分支、`scenario/*` Tags | 已完成 |
| 计划基线 | Milestone #1、Issues #3-#8 | 已完成 |
| 模板与责任人 | Issue Forms、PR Template、CODEOWNERS | 已合入 PR #1 |
| CI 初次失败与修复 | PR #1 的浅克隆/remote ref 失败和后续成功 Runs | 已完成 |
| 正常性能开发 | Issue #7、PR #10、4 项通过检查、Squash Merge | 已完成 |
| 缺陷首次修复失败 | Issue #5、PR #9、`available=-1` Check Run | 已保留 |
| Review 驳回与专家规则 | PR #13 Changes Requested、行级 Thread、知识文档 ID | 已完成 |
| 修复、复审与批准 | PR #13、提交 `72fb930`、线程解决、APPROVED、Merge | 已完成 |
| 计划外变更识别 | PR #14 无 Issue、`unplanned-change` 标签、Issue #15 补登记 | 已完成 |
| 分支保护 | Required Checks、严格同步、线程必须解决、禁止 force push | 已启用 |
| Hotfix 与 Revert | Issue #16、PR #17、精确回滚 PR #14 | 已完成 |
| Tag 与 Release | `v2.6.0-rc.1`、`v2.6.0-rc.2` GitHub Releases | 已完成 |
| 依赖自动更新 | Dependabot 自动创建 PR | 已启用 |
| Project 看板 | GitHub Projects v2 | CLI Token 尚缺 `read:project/project` 授权 |

## 核心对象

- Milestone：<https://github.com/pipiwolve/dumate-ecommerce-case/milestone/1>
- BUG-102 Issue：<https://github.com/pipiwolve/dumate-ecommerce-case/issues/5>
- 首次失败 PR：<https://github.com/pipiwolve/dumate-ecommerce-case/pull/9>
- 完整评审 PR：<https://github.com/pipiwolve/dumate-ecommerce-case/pull/13>
- 行级 Review Thread：<https://github.com/pipiwolve/dumate-ecommerce-case/pull/13#discussion_r3726405955>
- 计划外变更 PR：<https://github.com/pipiwolve/dumate-ecommerce-case/pull/14>
- HOTFIX-107：<https://github.com/pipiwolve/dumate-ecommerce-case/issues/16>
- Revert PR：<https://github.com/pipiwolve/dumate-ecommerce-case/pull/17>
- RC1：<https://github.com/pipiwolve/dumate-ecommerce-case/releases/tag/v2.6.0-rc.1>
- RC2：<https://github.com/pipiwolve/dumate-ecommerce-case/releases/tag/v2.6.0-rc.2>

## 不可变 Diff 证据

开发分支可以在 PR 合并后删除，所以 DuMate 的冻结快照使用以下 Tags，而不是依赖
可变分支：

- `scenario/feat-101`
- `scenario/bug-103`
- `scenario/bug-102-first-attempt`
- `scenario/bug-102-fixed`
- `scenario/perf-104`
- `scenario/chore-106`
- `scenario/hotfix-107`

其中 FEAT-101 和 BUG-103 是远程仓库创建前已经存在的历史 Commit，GitHub 上有真实
Commit URL，但没有伪造回溯 PR。联网后产生的 PR、Review、Check、Merge 与 Release
均为真实 GitHub 对象。
