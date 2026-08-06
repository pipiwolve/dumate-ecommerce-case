"""Knowledge and expert MCP for the ShopFlow delivery case."""

from __future__ import annotations

import os
from typing import Any, Awaitable, Callable

from fastmcp import FastMCP

from .knowledge import get_document, match_experts, search_knowledge


PRINCIPAL = os.getenv("MCP_PRINCIPAL", "principal_delivery")
EXPECTED_TOKEN = os.getenv("MCP_AUTH_TOKEN")
mcp = FastMCP("shopflow-knowledge-experts")


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
