"""MCP-related FastAPI routes"""
from fastapi import Request
from mcp.server.sse import SseServerTransport
from src.mcp_server.server import mcp_server
from src.config import SSE_ENDPOINT

# Initialize SSE transport
transport = SseServerTransport(SSE_ENDPOINT)


async def handle_sse(request: Request):
    """Handle SSE connections for MCP"""
    async with transport.connect_sse(
        request.scope, request.receive, request._send
    ) as (read_stream, write_stream):
        await mcp_server.run(
            read_stream, write_stream, mcp_server.create_initialization_options()
        )


async def handle_messages(request: Request):
    """Handle POST messages for MCP"""
    await transport.handle_post_message(request.scope, request.receive, request._send)
    return {"status": "ok"}
