"""Generate synchronized PPT reports and simulate audience-specific delivery."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .knowledge import get_document, match_experts
from .scenario import ROOT, build_snapshot, load_frozen_snapshot


OUTPUT_DIR = ROOT / "output" / "reports"
RUNTIME_DIR = ROOT / ".presentation-runtime"
REPOSITORY_RAW_BASE = (
    "https://github.com/pipiwolve/dumate-ecommerce-case/raw/refs/heads/main/output/reports"
)
REPORT_FILENAMES = [
    "ShopFlow-v2.6-技术负责人版.pptx",
    "ShopFlow-v2.6-客户项目经理版.pptx",
]


def pre_generated_reports() -> dict[str, Any]:
    """Return immutable demo artifacts without writing to the server filesystem."""

    snapshot = load_frozen_snapshot()
    audiences = ["tech_lead", "customer_project_manager"]
    reports = [
        {
            "audience": audience,
            "filename": filename,
            "url": f"{REPOSITORY_RAW_BASE}/{filename}",
        }
        for audience, filename in zip(audiences, REPORT_FILENAMES, strict=True)
    ]
    return {
        "snapshot_id": snapshot["snapshot_id"],
        "snapshot_at": snapshot["project"]["snapshot_at"],
        "reports": reports,
        "status": "pre_generated",
        "note": "Vercel 公网演示返回仓库内预生成制品，不在 Serverless 请求中生成文件。",
    }


def build_report_context() -> dict[str, Any]:
    context = build_snapshot(write=True)
    context["enrichment"] = {
        "primary_knowledge": get_document("principal_engineering", "kb-inventory-concurrency-v1"),
        "incident_knowledge": get_document("principal_engineering", "kb-incident-oversell-2025"),
        "release_policy": get_document("principal_customer_pm", "kb-release-gate-v1"),
        "primary_expert": match_experts(
            ["inventory", "concurrency", "oversell"],
            ["inventory-reservation"],
        )[0],
    }
    return context


def _find_presentation_skill() -> Path:
    configured = os.getenv("PRESENTATIONS_SKILL_DIR")
    if configured:
        return Path(configured)
    root = Path.home() / ".codex" / "plugins" / "cache" / "openai-primary-runtime" / "presentations"
    candidates = sorted(root.glob("*/skills/presentations"), reverse=True)
    if not candidates:
        raise RuntimeError("Presentations skill runtime not found; set PRESENTATIONS_SKILL_DIR")
    return candidates[0]


def _node_binary() -> str:
    configured = os.getenv("CODEX_NODE_BINARY")
    if configured:
        return configured
    node = shutil.which("node")
    if not node:
        raise RuntimeError("Node.js not found; set CODEX_NODE_BINARY")
    return node


def generate_reports() -> dict[str, Any]:
    context = build_report_context()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    skill_dir = _find_presentation_skill()
    node = _node_binary()
    setup_script = skill_dir / "container_tools" / "setup_artifact_tool_workspace.mjs"
    subprocess.run([node, str(setup_script), "--workspace", str(RUNTIME_DIR)], check=True)

    context_path = RUNTIME_DIR / "report-context.json"
    builder_path = RUNTIME_DIR / "report_builder.mjs"
    context_path.write_text(json.dumps(context, ensure_ascii=False, indent=2), encoding="utf-8")
    shutil.copyfile(ROOT / "presentation" / "report_builder.mjs", builder_path)
    subprocess.run([node, str(builder_path), str(context_path), str(OUTPUT_DIR)], check=True)

    files = [OUTPUT_DIR / filename for filename in REPORT_FILENAMES]
    if not all(file.exists() and file.stat().st_size > 0 for file in files):
        raise RuntimeError("report generation did not produce both PPTX files")
    metadata = {
        "snapshot_id": context["snapshot_id"],
        "snapshot_at": context["project"]["snapshot_at"],
        "reports": [str(file) for file in files],
        "status": "generated",
    }
    (OUTPUT_DIR / "generation.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return metadata


def simulate_push() -> dict[str, Any]:
    generation = generate_reports()
    targets = {
        "tech_lead": ROOT / "output" / "inbox" / "tech-lead",
        "customer_project_manager": ROOT / "output" / "inbox" / "customer-project-manager",
    }
    report_paths = [Path(path) for path in generation["reports"]]
    deliveries = []
    for (audience, directory), source in zip(targets.items(), report_paths, strict=True):
        directory.mkdir(parents=True, exist_ok=True)
        target = directory / source.name
        shutil.copy2(source, target)
        digest = hashlib.sha256(target.read_bytes()).hexdigest()
        deliveries.append(
            {
                "audience": audience,
                "file": str(target),
                "sha256": digest,
                "status": "delivered",
            }
        )
    log = {
        "task": "shopflow-weekly-delivery-update",
        "mode": "demo_auto_push",
        "snapshot_id": generation["snapshot_id"],
        "delivered_at": datetime.now(UTC).isoformat(),
        "deliveries": deliveries,
    }
    log_path = ROOT / "output" / "inbox" / "delivery-log.json"
    log_path.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")
    return {**log, "log_path": str(log_path)}
