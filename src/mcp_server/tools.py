"""MCP Tool definitions"""

import json
import mcp.types as types
from .server import mcp_server
from src.services.course_service import CourseService
from src.services.calendar_service import CalendarService


@mcp_server.list_tools()
async def list_tools() -> list[types.Tool]:
    """List available MCP tools"""
    return [
        types.Tool(
            name="get_filtered_courses",
            description="Retrieves and filters courses for a specific student. Returns all courses if no filters are provided, or filters by course code and/or week number when specified. Useful for querying student enrollment and course schedules, assignments, and deadlines.",
            inputSchema={
                "type": "object",
                "properties": {
                    "student_id": {
                        "type": "string",
                        "description": "Unique identifier of the student (required)",
                    },
                    "course_code": {
                        "type": "string",
                        "description": "Optional course code to filter results (e.g., 'CS101', 'MATH200')",
                    },
                    "week": {
                        "type": "string",
                        "description": "Optional week number to filter course content (e.g., '1', '5', '7')",
                    },
                },
                "required": ["student_id"],
            },
        ),
        types.Tool(
            name="build_ics_file",
            description="Builds an ICS file for calendar integration based on filtered courses and assignments.",
            inputSchema={
                "type": "object",
                "properties": {
                    "student_id": {
                        "type": "string",
                        "description": "Unique identifier of the student (required)",
                    },
                    "course_code": {
                        "type": "string",
                        "description": "Optional course code to filter results (e.g., 'CS101', 'MATH200')",
                    },
                    "week": {
                        "type": "string",
                        "description": "Optional week number to filter course content (e.g., '1', '5', '7')",
                    },
                },
                "required": ["student_id"],
            },
        ),
    ]


@mcp_server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """
    Execute an MCP tool

    Args:
        name: Tool name
        arguments: Tool arguments

    Returns:
        List of TextContent results
    """
    if name == "get_filtered_courses":
        result = await get_filtered_courses(arguments)

        return [
            types.TextContent(
                type="text", text=json.dumps(result, ensure_ascii=False, indent=2)
            )
        ]

    if name == "build_ics_file":
        ics_data = await build_ics_file(arguments)
        return [types.TextContent(type="text", text=ics_data)]

    raise ValueError(f"Herramienta desconocida: {name}")


async def build_ics_file(arguments: dict) -> str:
    student_id = arguments.get("student_id")
    course_code = arguments.get("course_code")
    week = arguments.get("week")

    # Fetch courses
    courses_data = CourseService.fetch_courses(student_id)

    # Build ICS calendar
    ics_data = CalendarService.build_ics_calendar(courses_data, course_code, week)

    return ics_data


async def get_filtered_courses(arguments) -> dict:
    student_id = arguments.get("student_id")
    course_code = arguments.get("course_code")
    week = arguments.get("week")

    # Fetch courses
    courses_data = CourseService.fetch_courses(student_id)

    # Filter by course_code if provided
    if course_code:
        courses_data = CourseService.filter_by_course_code(courses_data, course_code)

    # Format response
    result = CourseService.format_course_response(courses_data, week=week)

    return result
