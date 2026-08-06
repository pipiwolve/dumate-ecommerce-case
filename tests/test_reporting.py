from shopflow.reporting import build_report_context


def test_both_audiences_share_one_enriched_snapshot():
    context = build_report_context()
    assert context["snapshot_id"].startswith("shopflow-")
    assert context["enrichment"]["primary_expert"]["expert_id"] == "expert-wang-hai"
    assert context["enrichment"]["release_policy"]["classification"] == "public"

