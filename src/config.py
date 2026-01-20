"""Configuration settings for the MCP Student Server"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API URL
COURSES_API_URL = os.getenv("COURSES_API_URL", "")

# MCP Server configuration
MCP_SERVER_NAME = os.getenv("MCP_SERVER_NAME", "student-ai-server")

# FastAPI configuration
API_TITLE = "MCP Student Server"
API_VERSION = "1.0.0"
MCP_ENDPOINT = "/mcp"  # Streamable HTTP endpoint para Copilot Studio

# Redis Configuration
AzureForRedisHost = os.getenv("AzureForRedisHost", "")
AzureForRedisPort = os.getenv("AzureForRedisPort", "")
AzureForRedisPassword = os.getenv("AzureForRedisPassword", "")
