# Tool and Output Contract

## Required report context fields

- `report_context_id`, repository, Milestone, timezone, window start, window end
- Issues with status, owner, labels, source URL, and completion evidence
- PRs with base/head refs, SHA, Reviews, Check Runs, changed files, and affected modules
- unlinked changes and evidence gaps
- knowledge results with document ID, version, stable `source_url`, and `content_hash`
- expert results with `expert_id`, match reason, availability, and escalation condition
- facts, inferences, and pending confirmations stored separately

## MCP responsibility

GitHub official MCP supplies all repository and delivery facts. ShopFlow MCP exposes only:

1. `knowledge_search`
2. `knowledge_get_document`
3. `expert_match`

DuMate owns scheduling, context assembly, PPT generation, consistency checks, approval, and push.

## Enrichment order

For each material risk:

1. Derive risk tags and affected modules from GitHub evidence.
2. Call `knowledge_search` with the risk terms.
3. Call `knowledge_get_document` for the best authorized result.
4. Call `expert_match` with the same risk tags and affected modules.
5. Retain source, version, hash, match reason, availability, and escalation condition.

## Report invariants

- Both reports must show the same `report_context_id`, repository, Milestone, and time window.
- The technical report includes code-level evidence, CI, Reviews, knowledge, and expert routing.
- The customer report includes progress, business impact, recovery action, owner, and decisions.
- Every risk includes owner, next action, and evidence source.
- Mark inferred schedule impact as `待项目经理确认`.
- Production customer delivery requires human approval.
