import asyncio

from fastmcp import Client
from starlette.testclient import TestClient

from shopflow.mcp_server import app, mcp, mcp_app


def test_mcp_http_app_is_asgi_callable():
    assert callable(mcp_app)
    assert callable(app)


def test_mcp_exposes_only_knowledge_and_expert_tools():
    async def list_tool_names():
        async with Client(mcp) as client:
            return {tool.name for tool in await client.list_tools()}

    assert asyncio.run(list_tool_names()) == {
        "knowledge_search",
        "knowledge_get_document",
        "expert_match",
    }


def test_vercel_rewrite_path_accepts_mcp_initialize():
    with TestClient(app) as client:
        response = client.post(
            "/api/index.py",
            headers={"accept": "application/json, text/event-stream"},
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-06-18",
                    "capabilities": {},
                    "clientInfo": {"name": "vercel-path-test", "version": "1.0"},
                },
            },
        )

    assert response.status_code == 200
    assert response.json()["result"]["serverInfo"]["name"] == "shopflow-knowledge-experts"
