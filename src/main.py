"""Main entry point for the MCP Student Server"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from fastapi import FastAPI
from src.config import API_TITLE, API_VERSION
from src.routes.mcp_routes import handle_sse, handle_messages

# Import MCP components to register decorators
import src.mcp_server.resources  # noqa: F401
import src.mcp_server.tools  # noqa: F401

# Initialize FastAPI app
app = FastAPI(title=API_TITLE, version=API_VERSION)


# Register routes
@app.get("/sse")
async def sse_endpoint(request):
    """SSE endpoint for MCP connections"""
    return await handle_sse(request)


@app.post("/messages")
async def messages_endpoint(request):
    """Messages endpoint for MCP"""
    return await handle_messages(request)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": API_TITLE,
        "version": API_VERSION,
        "status": "running"
    }


# STDIO Entry Point for MCP Inspector
async def main():
    """Main entry point for STDIO mode (used by MCP Inspector)"""
    from mcp.server.stdio import stdio_server
    from src.mcp_server.server import mcp_server

    async with stdio_server() as (read_stream, write_stream):
        await mcp_server.run(
            read_stream, write_stream, mcp_server.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
