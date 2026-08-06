---
name: ecommerce-delivery-review
description: Review a software delivery milestone from GitHub Issue, PR, Commit, Diff, Review, and Check evidence; enrich risks with cited internal knowledge and matched human experts; then generate synchronized technical-lead and customer-project-manager reports. Use for ShopFlow delivery status, release-risk reviews, scheduled project updates, code-change impact summaries, or dual-audience PPT generation.
---

# Ecommerce Delivery Review

Create one shared report context and derive both audience reports from it. Treat the GitHub Project
or Milestone and its Issues as the plan baseline. Treat code activity only as evidence.

Read [references/contracts.md](references/contracts.md) before invoking tools.

## Workflow

1. Resolve exactly one repository, Milestone, time window, and timezone.
2. Use the DuMate GitHub MCP to list Milestone Issues, linked PRs, Reviews, Check Runs, Commits,
   and changed files. Preserve item URLs and SHAs.
3. Normalize official GitHub MCP results into one report context. Do not use repository fixture data
   as the current state.
4. Flag code changes with no Issue link as unplanned. Flag closed Issues without code, tests,
   documents, or acceptance evidence as evidence gaps.
5. Calculate progress using Issue weights and progress fields. Never use commit count, lines changed,
   or PR count as delivery progress.
6. For each blocker or material risk, call `knowledge_search`; read the best document with
   `knowledge_get_document`; retain source URL, version, anchor, and content hash.
7. Call `expert_match` with risk tags and affected modules. Recommend people with the match reason
   and escalation condition. Do not present a Skill as a human expert.
8. Separate facts, inferences, and pending confirmations. A failed check is a fact; a release delay
   is an inference unless the due date is already missed or an authorized owner confirms it.
9. Generate both PPT files with DuMate from the shared context. Verify that both contain the same
   context ID and time window.
10. Push the technical report to the internal owner. In the demo, push the customer report directly;
    in production, require approval and keep an unapproved customer report internal.

## Audience Rules

- Technical lead: include Issue and PR identifiers, SHA, failed assertion, affected modules, Diff
  scale, review decision, knowledge evidence, expert match, and concrete engineering actions.
- Customer project manager: include milestone progress, completed outcomes, blocker impact, owner,
  recovery action, and decision required. Exclude internal blame, raw stack traces, sensitive
  incident details, and speculative delivery commitments.

## Failure Handling

- Stop and report authorization failures; never replace them with an empty list.
- Mark a source unavailable on timeout and keep the report context incomplete. Do not fabricate status.
- Do not generate reports if GitHub and Git evidence refer to different heads or snapshot times.
- Keep customer-facing delivery dates as pending confirmation unless an authorized owner supplied
  them.
