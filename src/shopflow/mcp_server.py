"""Knowledge, expert, snapshot, and reporting MCP for the ShopFlow case."""

from __future__ import annotations

import os
from typing import Any

from fastmcp import FastMCP

from .knowledge import get_document, match_experts, search_knowledge
from .reporting import generate_reports, simulate_push
from .scenario import build_snapshot, get_issue


PRINCIPAL = os.getenv("MCP_PRINCIPAL", "principal_engineering")
mcp = FastMCP("shopflow-delivery-knowledge")


@mcp.tool()
def delivery_build_snapshot() -> dict[str, Any]:
    """Freeze the local Git and GitHub-compatible evidence into one cited snapshot."""

    return build_snapshot(write=True)


@mcp.tool()
def delivery_get_issue(issue_key: str) -> dict[str, Any]:
    """Read one normalized issue from the current delivery evidence."""

    return get_issue(issue_key)


@mcp.tool()
def knowledge_search(query: str, document_type: str | None = None) -> list[dict[str, Any]]:
    """Search authorized ShopFlow knowledge with stable source URLs."""

    return search_knowledge(PRINCIPAL, query, document_type)


@mcp.tool()
def knowledge_get_document(document_id: str, max_chars: int = 4000) -> dict[str, Any]:
    """Read a bounded excerpt and content hash for an authorized document."""

    return get_document(PRINCIPAL, document_id, max_chars)


@mcp.tool()
def expert_match(risk_tags: list[str], modules: list[str] | None = None) -> list[dict[str, Any]]:
    """Rank human experts by risk domain and affected module."""

    return match_experts(risk_tags, modules)


@mcp.tool()
def delivery_generate_reports() -> dict[str, Any]:
    """Generate synchronized technical-lead and customer-project-manager PPTX files."""

    return generate_reports()


@mcp.tool()
def delivery_simulate_push() -> dict[str, Any]:
    """Generate and copy both reports into separate local demo inboxes."""

    return simulate_push()



mcp_app = mcp.http_app(
    path="/mcp",
    transport="streamable-http",
    stateless_http=True,
    json_response=True,
)


if __name__ == "__main__":
    transport = os.getenv("MCP_TRANSPORT", "stdio")
    if transport == "streamable-http":
        mcp.run(
            transport="streamable-http",
            host=os.getenv("MCP_HOST", "127.0.0.1"),
            port=int(os.getenv("MCP_PORT", "8130")),
            path="/mcp",
        )
    else:
        mcp.run()
