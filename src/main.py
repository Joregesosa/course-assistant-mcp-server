"""Main entry point for the MCP Student Server"""
import sys
import logging
from pathlib import Path
from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import Response
from src.config import API_TITLE, API_VERSION
from src.routes.mcp_routes import handle_streamable_http, mcp_lifespan

# Import MCP components to register decorators
import src.mcp_server.resources  # noqa: F401
import src.mcp_server.tools  # noqa: F401

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Initialize FastAPI app with lifespan
app = FastAPI(title=API_TITLE, version=API_VERSION, lifespan=mcp_lifespan)

# Add CORS middleware for Copilot Studio
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ajustar según tus necesidades de seguridad
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Mcp-Session-Id"],  # Importante para MCP
)


# Register MCP endpoint directly (sin Mount para evitar redirect)
@app.post("/mcp")
async def mcp_endpoint(request: Request):
    """MCP Streamable HTTP endpoint for Copilot Studio"""
    import logging
    logger = logging.getLogger(__name__)
    
    # Log del request para debugging
    body = await request.body()
    logger.info(f"Received POST /mcp - Content-Type: {request.headers.get('content-type')}")
    logger.info(f"Body length: {len(body)}")
    logger.info(f"Body: {body[:500]}")  # Primeros 500 bytes
    
    # Capturar headers y body de la respuesta
    response_headers = {}
    response_body = []
    status_code = 200
    
    async def send_wrapper(message):
        nonlocal status_code
        if message["type"] == "http.response.start":
            status_code = message.get("status", 200)
            for header_name, header_value in message.get("headers", []):
                response_headers[header_name.decode()] = header_value.decode()
        elif message["type"] == "http.response.body":
            body = message.get("body", b"")
            if body:
                response_body.append(body)
    
    # Necesitamos recrear el receive porque ya leímos el body
    async def receive_wrapper():
        return {
            "type": "http.request",
            "body": body,
            "more_body": False
        }
    
    await handle_streamable_http(request.scope, receive_wrapper, send_wrapper)
    
    # Log de la respuesta
    content = b"".join(response_body)
    logger.info(f"Response status: {status_code}")
    logger.info(f"Response body: {content[:500]}")
    
    # Construir la respuesta con los headers correctos
    return Response(
        content=content,
        status_code=status_code,
        headers=response_headers
    )


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
