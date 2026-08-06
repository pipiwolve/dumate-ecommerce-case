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
        snapshot_result = await client.call_tool("delivery_build_snapshot", {})
        knowledge_result = await client.call_tool(
            "knowledge_search", {"query": "inventory concurrency oversell"}
        )
        expert_result = await client.call_tool(
            "expert_match",
            {
                "risk_tags": ["inventory", "concurrency", "oversell"],
                "modules": ["inventory-reservation"],
            },
        )
        reports_result = await client.call_tool("delivery_generate_reports", {})
        push_result = await client.call_tool("delivery_simulate_push", {})
        payload = snapshot_result.data
        print(
            json.dumps(
                {
                    "url": url,
                    "tools": [tool.name for tool in tools],
                    "snapshot_id": payload["snapshot_id"],
                    "health": payload["metrics"]["health"],
                    "knowledge": knowledge_result.data[0]["document_id"],
                    "expert": expert_result.data[0]["expert_id"],
                    "reports_status": reports_result.data["status"],
                    "report_count": len(reports_result.data["reports"]),
                    "push_status": push_result.data["status"],
                },
                ensure_ascii=False,
                indent=2,
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
