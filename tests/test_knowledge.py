import pytest

from shopflow.knowledge import get_document, match_experts, search_knowledge


def test_concurrency_search_returns_cited_internal_standard():
    result = search_knowledge("principal_engineering", "inventory concurrency oversell")
    assert result[0]["document_id"] == "kb-inventory-concurrency-v1"
    assert result[0]["source_url"].startswith("kb://")


def test_customer_pm_cannot_read_restricted_incident():
    assert search_knowledge("principal_customer_pm", "oversell incident") == []
    with pytest.raises(PermissionError):
        get_document("principal_customer_pm", "kb-incident-oversell-2025")


def test_inventory_concurrency_risk_matches_primary_expert():
    result = match_experts(["inventory", "concurrency", "oversell"], ["inventory-reservation"])
    assert result[0]["expert_id"] == "expert-wang-hai"
    assert result[0]["score"] >= 9

