"""Configuration settings for the MCP Student Server"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Data configuration
DATA_FILE_PATH = os.getenv("DATA_FILE_PATH", str(BASE_DIR / "data" / "example_data.json"))

# API URL
COURSES_API_URL = os.getenv("COURSES_API_URL", "")

# MCP Server configuration
MCP_SERVER_NAME = os.getenv("MCP_SERVER_NAME", "student-ai-server")
DEFAULT_STUDENT_ID = os.getenv("DEFAULT_STUDENT_ID", "30040229")  # Student ID por defecto para pruebas

# FastAPI configuration
API_TITLE = "MCP Student Server"
API_VERSION = "1.0.0"
MCP_ENDPOINT = "/mcp"  # Streamable HTTP endpoint para Copilot Studio
