"""Build a normalized delivery snapshot from GitHub-compatible seed data and Git."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SEED_PATH = ROOT / "scenario" / "github" / "seed.json"
SNAPSHOT_DIR = ROOT / "output" / "snapshots"


def _git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _modules(files: list[str]) -> list[str]:
    mapping = {
        "src/shopflow/inventory.py": "inventory-reservation",
        "src/shopflow/orders.py": "order-service",
        "src/shopflow/cart.py": "cart-service",
        "src/shopflow/admin.py": "admin-console",
        "config/": "runtime-config",
        "tests/": "quality-gates",
    }
    found = []
    for file in files:
        for prefix, module in mapping.items():
            if file == prefix or file.startswith(prefix):
                if module not in found:
                    found.append(module)
    return found or ["repository-infrastructure"]


def _diff(base_ref: str, head_ref: str) -> dict[str, Any]:
    empty_tree = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"
    diff_args = (empty_tree, head_ref) if base_ref == "EMPTY" else (f"{base_ref}...{head_ref}",)
    files = [line for line in _git("diff", "--name-only", *diff_args).splitlines() if line]
    insertions = 0
    deletions = 0
    for line in _git("diff", "--numstat", *diff_args).splitlines():
        added, removed, _ = line.split("\t", 2)
        if added.isdigit():
            insertions += int(added)
        if removed.isdigit():
            deletions += int(removed)
    return {
        "base_ref": base_ref,
        "head_ref": head_ref,
        "head_sha": _git("rev-parse", head_ref),
        "files": files,
        "modules": _modules(files),
        "insertions": insertions,
        "deletions": deletions,
        "source_url": f"git://shopflow/{base_ref}...{head_ref}",
    }


def load_seed() -> dict[str, Any]:
    return json.loads(SEED_PATH.read_text(encoding="utf-8"))


def build_snapshot(write: bool = True) -> dict[str, Any]:
    seed = load_seed()
    pull_requests = []
    for item in seed["pull_requests"]:
        pull_requests.append({**item, "diff": _diff(item["base_ref"], item["head_ref"])})

    findings = []
    for item in seed["findings"]:
        findings.append({**item, "diff": _diff("scenario/product-main", item["head_ref"])})

    weighted_progress = sum(
        issue["weight"] * issue["progress"] / 100 for issue in seed["issues"]
    )
    total_weight = sum(issue["weight"] for issue in seed["issues"])
    progress = round(weighted_progress / total_weight * 100) if total_weight else 0
    blockers = [issue["key"] for issue in seed["issues"] if issue["status"] == "阻塞"]
    snapshot = {
        "schema_version": "1.0",
        "project": seed["project"],
        "metrics": {
            "weighted_progress": progress,
            "health": "at_risk" if blockers else "on_track",
            "open_issues": sum(issue["state"] == "open" for issue in seed["issues"]),
            "closed_issues": sum(issue["state"] == "closed" for issue in seed["issues"]),
            "release_blockers": blockers,
            "open_pull_requests": sum(pr["state"] == "open" for pr in pull_requests),
            "failed_checks": sum(
                check["conclusion"] == "failure"
                for pr in pull_requests
                for check in pr["checks"]
            ),
            "unlinked_changes": len(findings),
        },
        "issues": seed["issues"],
        "pull_requests": pull_requests,
        "findings": findings,
        "sources": [
            {"type": "github", "uri": "github://pipiwolve/dumate-ecommerce-case/milestone/v2.6"},
            {"type": "git", "uri": f"git://shopflow/product-main@{_git('rev-parse', 'scenario/product-main')}"},
            {"type": "scenario", "uri": str(SEED_PATH.relative_to(ROOT))},
        ],
    }
    canonical = json.dumps(snapshot, ensure_ascii=False, sort_keys=True).encode("utf-8")
    snapshot["snapshot_id"] = f"shopflow-{hashlib.sha256(canonical).hexdigest()[:12]}"
    if write:
        SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
        target = SNAPSHOT_DIR / "snapshot-2026-08-06.json"
        target.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
        snapshot["output_path"] = str(target)
    return snapshot


def get_issue(issue_key: str) -> dict[str, Any]:
    snapshot = build_snapshot(write=False)
    try:
        return next(issue for issue in snapshot["issues"] if issue["key"] == issue_key)
    except StopIteration as exc:
        raise LookupError(f"issue {issue_key} not found") from exc
