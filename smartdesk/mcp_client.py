
"""MCP client for SmartDesk tools."""

import json
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def call_mcp_tool(name: str, arguments: dict):
    allowed = {
        "get_order_details",
        "lookup_policy",
        "draft_support_ticket",
    }

    if name not in allowed:
        raise ValueError("Tool not allowed")

    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "smartdesk.mcp_server"],
    )

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.call_tool(name, arguments)

            if result.isError:
                raise RuntimeError(f"MCP tool failed: {name}")

            if result.structuredContent is not None:
                return result.structuredContent

            content = "\n".join(
                getattr(part, "text", "")
                for part in result.content
            )

            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return content
