"""MCP-related FastAPI routes"""
import contextlib
from collections.abc import AsyncIterator
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from starlette.types import Receive, Scope, Send
from src.mcp_server.server import mcp_server

# Initialize StreamableHTTP session manager with JSON responses for Copilot Studio
session_manager = StreamableHTTPSessionManager(
    app=mcp_server,
    json_response=True,  # Importante: JSON responses para Copilot Studio
    stateless=True  # Stateless para mejor escalabilidad
)


async def handle_streamable_http(scope: Scope, receive: Receive, send: Send) -> None:
    """Handle StreamableHTTP requests for MCP"""
    await session_manager.handle_request(scope, receive, send)


@contextlib.asynccontextmanager
async def mcp_lifespan(app) -> AsyncIterator[None]:
    """Lifespan context manager for MCP session manager"""
    async with session_manager.run():
        yield
