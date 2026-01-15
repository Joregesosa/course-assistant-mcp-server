"""Configuration settings for the MCP Student Server"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Data configuration
DATA_FILE_PATH = os.getenv("DATA_FILE_PATH", str(BASE_DIR / "data" / "example_data.json"))

# MCP Server configuration
MCP_SERVER_NAME = os.getenv("MCP_SERVER_NAME", "estudiante-ai-server")

# FastAPI configuration
API_TITLE = "MCP Student Server"
API_VERSION = "1.0.0"
SSE_ENDPOINT = "/messages"
