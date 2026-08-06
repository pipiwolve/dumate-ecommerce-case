# Tool and Output Contract

## Required snapshot fields

- `snapshot_id`, `schema_version`, and `project.snapshot_at`
- repository and Milestone identity
- weighted progress and health
- Issues with status, weight, progress, owner, labels, and source
- PRs with base/head refs, SHA, Reviews, Check Runs, changed files, and affected modules
- unlinked changes and evidence gaps
- knowledge results with stable `source_url` and `content_hash`
- expert results with `expert_id`, match reason, availability, and escalation condition

## Demo tool order

1. `delivery_build_snapshot`
2. `knowledge_search(query="inventory concurrency oversell")`
3. `knowledge_get_document(document_id="kb-inventory-concurrency-v1")`
4. `expert_match(risk_tags=["inventory", "concurrency", "oversell"], modules=["inventory-reservation"] )`
5. `delivery_generate_reports`
6. `delivery_simulate_push`

## Report invariants

- Both reports must show the same snapshot ID and snapshot time.
- The technical report may cite restricted engineering knowledge.
- The customer report may cite only customer-visible policy and Milestone evidence.
- Every risk must include owner, next action, and evidence source.
- Mark inferred schedule impact as `待项目经理确认`.

