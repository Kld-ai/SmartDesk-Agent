
"""SmartDesk MCP server with three tools."""

from mcp.server.fastmcp import FastMCP
from .storage import get_order, policy
from .security import redact

mcp = FastMCP("smartdesk-server")


@mcp.tool()
def get_order_details(order_id: str) -> dict:
    """Retrieve a synthetic customer order by its order ID."""
    return get_order(order_id)


@mcp.tool()
def lookup_policy(topic: str) -> str:
    """Look up store policies for shipping, returns and refunds."""
    return policy(topic)[:1800]


@mcp.tool()
def draft_support_ticket(order_id: str, issue: str) -> dict:
    """Prepare a support ticket draft without writing any data."""
    order = get_order(order_id)

    if "error" in order:
        return {"error": "unknown_order"}

    return {
        "status": "awaiting_human_approval",
        "order_id": order_id,
        "issue": redact(issue),
        "write_performed": False,
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")
