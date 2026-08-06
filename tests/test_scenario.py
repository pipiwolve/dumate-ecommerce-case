from shopflow.scenario import build_snapshot


def test_snapshot_uses_real_git_refs_and_expected_delivery_health():
    snapshot = build_snapshot(write=False)
    assert snapshot["metrics"]["weighted_progress"] == 65
    assert snapshot["metrics"]["health"] == "at_risk"
    assert snapshot["metrics"]["release_blockers"] == ["BUG-102"]
    assert snapshot["metrics"]["failed_checks"] == 1
    assert snapshot["metrics"]["unlinked_changes"] == 1
    assert all(len(pr["diff"]["head_sha"]) == 40 for pr in snapshot["pull_requests"])
    assert snapshot["live_evidence"]["bug_102_final_pr"].endswith("/pull/13")
    assert snapshot["live_evidence"]["hotfix_107_pr"].endswith("/pull/17")
    assert snapshot["live_evidence"]["release_rc2"].endswith("/v2.6.0-rc.2")


def test_snapshot_detects_expected_affected_modules():
    snapshot = build_snapshot(write=False)
    bug_pr = next(pr for pr in snapshot["pull_requests"] if pr["number"] == 202)
    perf_pr = next(pr for pr in snapshot["pull_requests"] if pr["number"] == 204)
    assert "inventory-reservation" in bug_pr["diff"]["modules"]
    assert {"cart-service", "inventory-reservation"}.issubset(perf_pr["diff"]["modules"])
