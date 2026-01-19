"""MCP Resource definitions"""

import json
from datetime import datetime
import mcp.types as types
from .server import mcp_server
from src.services.course_service import CourseService


@mcp_server.list_resource_templates()
async def list_resource_templates() -> list[types.ResourceTemplate]:
    """Define resource templates for dynamic URI handling"""
    return [
        types.ResourceTemplate(
            uriTemplate="students://{student_id}/courses",
            name="Cursos del Estudiante",
            description="Recupera la lista de cursos para un ID de estudiante específico",
            mimeType="application/json",
        )
    ]


@mcp_server.list_resources()
async def list_resources() -> list[types.Resource]:
    """List available resources"""
    return [
        types.Resource(
            uri="students://example/courses",
            name="Cursos de Estudiante",
            description="Lista de cursos de un estudiante",
            mimeType="text/plain",
        )
    ]


@mcp_server.read_resource()
async def read_resource(uri: str) -> str:
    """
    Read a specific resource by URI

    Args:
        uri: Resource URI (e.g., students://123/courses)

    Returns:
        JSON string with course data
    """
    uri_str = str(uri)

    if uri_str.startswith("students://") and uri_str.endswith("/courses"):
        # Extract student ID dynamically
        student_id = uri_str.replace("students://", "").replace("/courses", "")

        # Fetch courses
        courses_data = CourseService().fetch_courses(student_id)
        basic_courses = CourseService.get_basic_course_info(courses_data)

        current_week = courses_data[0]["current_week"] if courses_data else "1"
        current_date = datetime.now().strftime("%d/%m/%Y")

        result = {
            "student_id": student_id,
            "current_week": current_week,
            "current_date": current_date,
            "courses": basic_courses,
        }

        return json.dumps(result, ensure_ascii=False, indent=2)

    raise ValueError("Recurso no encontrado")
