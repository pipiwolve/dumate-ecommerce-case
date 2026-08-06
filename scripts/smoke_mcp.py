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
        result = await client.call_tool("delivery_build_snapshot", {})
        payload = result.data
        print(
            json.dumps(
                {
                    "url": url,
                    "tools": [tool.name for tool in tools],
                    "snapshot_id": payload["snapshot_id"],
                    "health": payload["metrics"]["health"],
                },
                ensure_ascii=False,
                indent=2,
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
