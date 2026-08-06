"""Publish the repeatable ShopFlow scenario to a real GitHub repository.

The default mode is read-only and prints the planned actions. Use --apply only
after confirming the target account, repository visibility, and gh auth state.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "scenario" / "github" / "seed.json"


def command(args: list[str], apply: bool, capture: bool = False) -> str:
    printable = " ".join(args)
    if not apply:
        print(f"DRY-RUN  {printable}")
        return ""
    result = subprocess.run(args, cwd=ROOT, check=True, text=True, capture_output=capture)
    return result.stdout.strip() if capture else ""


def create_labels(repo: str, issues: list[dict[str, Any]], apply: bool) -> None:
    colors = {
        "bug": "D73A4A",
        "feature": "2E7CF6",
        "inventory": "0E8A16",
        "performance": "FBCA04",
        "security": "B60205",
        "release-blocker": "D93F0B",
        "release/v2.6": "5319E7",
    }
    labels = sorted({label for issue in issues for label in issue["labels"]})
    for label in labels:
        command(
            ["gh", "label", "create", label, "--repo", repo, "--color", colors.get(label, "D4C5F9"), "--force"],
            apply,
        )


def create_issue(repo: str, milestone: str, issue: dict[str, Any], apply: bool) -> str:
    body = (
        f"{issue['body']}\n\n"
        f"场景键：`{issue['key']}`\n"
        f"优先级：`{issue['priority']}`\n"
        f"负责人：{issue['assignee']}\n"
        f"进度：{issue['progress']}%"
    )
    args = [
        "gh", "issue", "create", "--repo", repo,
        "--title", f"[{issue['key']}] {issue['title']}",
        "--body", body,
        "--milestone", milestone,
    ]
    for label in issue["labels"]:
        args.extend(["--label", label])
    url = command(args, apply, capture=True)
    if not apply:
        return f"dry-run://{issue['key']}"
    for comment in issue["comments"]:
        command(
            ["gh", "issue", "comment", url, "--repo", repo, "--body", f"{comment['author']} / {comment['at']}\n\n{comment['body']}"],
            True,
        )
    if issue["state"] == "closed":
        command(["gh", "issue", "close", url, "--repo", repo, "--comment", "场景初始化：对应修复已进入 main。"], True)
    return url


def publish(repo: str, apply: bool) -> None:
    seed = json.loads(SEED.read_text(encoding="utf-8"))
    milestone = seed["project"]["milestone"]
    if apply:
        command(["gh", "auth", "status"], True)
    command(
        [
            "gh", "api", f"repos/{repo}/milestones", "--method", "POST",
            "-f", f"title={milestone['title']}",
            "-f", f"due_on={milestone['due_on']}T23:59:59Z",
            "-f", "description=ShopFlow v2.6 DuMate delivery demo",
        ],
        apply,
    )
    create_labels(repo, seed["issues"], apply)
    issue_urls = {
        issue["key"]: create_issue(repo, milestone["title"], issue, apply)
        for issue in seed["issues"]
    }

    for branch in ["fix/bug-102-oversell", "perf/perf-104-batch-stock", "chore/cache-tuning"]:
        command(["git", "push", "origin", branch], apply)
    for pr in seed["pull_requests"]:
        if pr["state"] != "open":
            continue
        related = ", ".join(f"{key}: {issue_urls[key]}" for key in pr["issue_keys"])
        github_base = "main" if pr["base_ref"].startswith("scenario/") else pr["base_ref"]
        command(
            [
                "gh", "pr", "create", "--repo", repo,
                "--base", github_base, "--head", pr["head_ref"],
                "--title", pr["title"],
                "--body", f"DuMate 场景 PR。关联事项：{related}",
            ],
            apply,
        )
    print("APPLIED" if apply else "Dry-run complete. Re-run with --apply after reviewing every target.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True, help="Target OWNER/REPO")
    parser.add_argument("--apply", action="store_true", help="Perform external GitHub writes")
    args = parser.parse_args()
    publish(args.repo, args.apply)


if __name__ == "__main__":
    main()
