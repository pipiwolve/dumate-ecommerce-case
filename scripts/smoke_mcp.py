"""Verify the running Streamable HTTP MCP endpoint."""

from __future__ import annotations

import asyncio
import json
import os

from fastmcp import Client


async def main() -> None:
    url = os.getenv("SHOPFLOW_MCP_URL", "http://127.0.0.1:8130/mcp")
    async with Client(url) as client:
        tools = await client.list_tools()
        knowledge_result = await client.call_tool(
            "knowledge_search", {"query": "inventory concurrency oversell"}
        )
        document_result = await client.call_tool(
            "knowledge_get_document",
            {"document_id": knowledge_result.data[0]["document_id"]},
        )
        expert_result = await client.call_tool(
            "expert_match",
            {
                "risk_tags": ["inventory", "concurrency", "oversell"],
                "modules": ["inventory-reservation"],
            },
        )
        print(
            json.dumps(
                {
                    "url": url,
                    "tools": [tool.name for tool in tools],
                    "knowledge": knowledge_result.data[0]["document_id"],
                    "document_hash": document_result.data["content_hash"],
                    "expert": expert_result.data[0]["expert_id"],
                },
                ensure_ascii=False,
                indent=2,
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
