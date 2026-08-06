"""Knowledge, expert, snapshot, and reporting MCP for the ShopFlow case."""

from __future__ import annotations

import os
from typing import Any, Awaitable, Callable

from fastmcp import FastMCP

from .knowledge import get_document, match_experts, search_knowledge
from .reporting import generate_reports, pre_generated_reports, simulate_push
from .scenario import build_snapshot, get_issue, load_frozen_snapshot


PRINCIPAL = os.getenv("MCP_PRINCIPAL", "principal_delivery")
SERVERLESS = os.getenv("VERCEL") == "1" or os.getenv("MCP_READ_ONLY") == "1"
EXPECTED_TOKEN = os.getenv("MCP_AUTH_TOKEN")
mcp = FastMCP("shopflow-delivery-knowledge")


@mcp.tool()
def delivery_build_snapshot() -> dict[str, Any]:
    """Freeze the local Git and GitHub-compatible evidence into one cited snapshot."""

    if SERVERLESS:
        return load_frozen_snapshot()
    return build_snapshot(write=True)


@mcp.tool()
def delivery_get_issue(issue_key: str) -> dict[str, Any]:
    """Read one normalized issue from the current delivery evidence."""

    if SERVERLESS:
        snapshot = load_frozen_snapshot()
        try:
            return next(issue for issue in snapshot["issues"] if issue["key"] == issue_key)
        except StopIteration as exc:
            raise LookupError(f"issue {issue_key} not found") from exc
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

    if SERVERLESS:
        return pre_generated_reports()
    return generate_reports()


@mcp.tool()
def delivery_simulate_push() -> dict[str, Any]:
    """Generate and copy both reports into separate local demo inboxes."""

    if SERVERLESS:
        reports = pre_generated_reports()
        return {
            "task": "shopflow-weekly-delivery-update",
            "mode": "public_demo_preview",
            "snapshot_id": reports["snapshot_id"],
            "deliveries": reports["reports"],
            "status": "simulated",
            "note": "公网演示不发送外部消息；实际业务上线后应接人工审核和受控推送通道。",
        }
    return simulate_push()



mcp_app = mcp.http_app(
    path="/mcp",
    transport="streamable-http",
    stateless_http=True,
    json_response=True,
)


class OptionalBearerAuth:
    """Require a deployment token only when MCP_AUTH_TOKEN is configured."""

    def __init__(self, asgi_app: Callable[..., Awaitable[None]]) -> None:
        self.asgi_app = asgi_app

    async def __call__(self, scope: dict[str, Any], receive: Callable, send: Callable) -> None:
        if EXPECTED_TOKEN and scope.get("path") == "/mcp":
            headers = dict(scope.get("headers", []))
            authorization = headers.get(b"authorization", b"").decode()
            if authorization != f"Bearer {EXPECTED_TOKEN}":
                await send(
                    {
                        "type": "http.response.start",
                        "status": 401,
                        "headers": [(b"content-type", b"application/json")],
                    }
                )
                await send({"type": "http.response.body", "body": b'{"error":"unauthorized"}'})
                return
        await self.asgi_app(scope, receive, send)


class VercelPathAdapter:
    """Normalize the function rewrite path before FastMCP route matching."""

    def __init__(self, asgi_app: Callable[..., Awaitable[None]]) -> None:
        self.asgi_app = asgi_app

    async def __call__(self, scope: dict[str, Any], receive: Callable, send: Callable) -> None:
        if scope.get("type") == "http" and scope.get("path") != "/mcp":
            normalized = dict(scope)
            normalized["path"] = "/mcp"
            normalized["raw_path"] = b"/mcp"
            await self.asgi_app(normalized, receive, send)
            return
        await self.asgi_app(scope, receive, send)


app = VercelPathAdapter(OptionalBearerAuth(mcp_app))


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
