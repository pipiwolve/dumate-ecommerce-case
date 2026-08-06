from shopflow import scenario
from shopflow.reporting import pre_generated_reports


def test_pre_generated_reports_share_the_frozen_snapshot(monkeypatch):
    def fail_if_git_is_called(*args):
        raise AssertionError(f"serverless report attempted Git access: {args}")

    monkeypatch.setattr(scenario, "_git", fail_if_git_is_called)
    payload = pre_generated_reports()

    assert payload["snapshot_id"] == "shopflow-fcbc6c1cd435"
    assert payload["status"] == "pre_generated"
    assert [item["audience"] for item in payload["reports"]] == [
        "tech_lead",
        "customer_project_manager",
    ]
    assert all(item["url"].startswith("https://github.com/") for item in payload["reports"])
