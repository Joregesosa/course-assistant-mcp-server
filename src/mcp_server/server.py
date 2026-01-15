"""MCP Server initialization"""
from mcp.server import Server
from src.config import MCP_SERVER_NAME

# Initialize the MCP server
mcp_server = Server(MCP_SERVER_NAME)
