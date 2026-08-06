"""Git-backed knowledge search and expert matching for the demo MCP."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
KNOWLEDGE_DIR = ROOT / "knowledge"
PUBLISHED_DIR = KNOWLEDGE_DIR / "published"


def _manifest() -> list[dict[str, Any]]:
    return json.loads((KNOWLEDGE_DIR / "manifest.json").read_text(encoding="utf-8"))


def _authorized(principal: str, item: dict[str, Any]) -> bool:
    if principal not in {"principal_engineering", "principal_delivery", "principal_customer_pm"}:
        raise PermissionError(f"unknown principal: {principal}")
    return principal in item["allowed_principals"]


def _terms(query: str) -> list[str]:
    return [term.lower() for term in re.findall(r"[\w+-]+", query) if len(term) > 1]


def search_knowledge(principal: str, query: str, document_type: str | None = None) -> list[dict[str, Any]]:
    terms = _terms(query)
    results = []
    for item in _manifest():
        if item["status"] != "published" or not _authorized(principal, item):
            continue
        if document_type and item["document_type"] != document_type:
            continue
        content = (PUBLISHED_DIR / item["filename"]).read_text(encoding="utf-8")
        haystack = " ".join([item["title"], *item["tags"], content]).lower()
        score = sum(haystack.count(term) for term in terms)
        if score:
            results.append(
                {
                    "document_id": item["document_id"],
                    "title": item["title"],
                    "document_type": item["document_type"],
                    "version": item["version"],
                    "source_url": item["source_url"],
                    "tags": item["tags"],
                    "score": score,
                }
            )
    return sorted(results, key=lambda result: (-result["score"], result["document_id"]))[:8]


def get_document(principal: str, document_id: str, max_chars: int = 4000) -> dict[str, Any]:
    try:
        item = next(entry for entry in _manifest() if entry["document_id"] == document_id)
    except StopIteration as exc:
        raise LookupError("document not found") from exc
    if not _authorized(principal, item):
        raise PermissionError("document is outside the principal's scope")
    content = (PUBLISHED_DIR / item["filename"]).read_text(encoding="utf-8")
    return {
        **item,
        "content_hash": hashlib.sha256(content.encode("utf-8")).hexdigest(),
        "excerpt": content[: max(500, min(max_chars, 8000))],
    }


def match_experts(risk_tags: list[str], modules: list[str] | None = None) -> list[dict[str, Any]]:
    requested = {tag.lower() for tag in risk_tags}
    affected_modules = set(modules or [])
    experts = json.loads((KNOWLEDGE_DIR / "experts.json").read_text(encoding="utf-8"))
    matches = []
    for expert in experts:
        domain_hits = sorted(requested.intersection(expert["domains"]))
        module_hits = sorted(affected_modules.intersection(expert["modules"]))
        score = len(domain_hits) * 3 + len(module_hits) * 2
        if score:
            matches.append(
                {
                    **expert,
                    "score": score,
                    "matched_domains": domain_hits,
                    "matched_modules": module_hits,
                    "match_reason": f"领域匹配 {', '.join(domain_hits) or '无'}；模块匹配 {', '.join(module_hits) or '无'}",
                    "source_url": f"directory://shopflow/experts/{expert['expert_id']}",
                }
            )
    return sorted(matches, key=lambda item: (-item["score"], item["expert_id"]))

