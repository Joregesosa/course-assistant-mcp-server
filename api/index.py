from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from mcp.server import Server
from mcp.server.sse import SseServerTransport
import mcp.types as types
from sse_starlette import EventSourceResponse
from datetime import datetime
import json
 # Create calendar
from icalendar import Calendar, Event
from datetime import datetime, timedelta
import pytz
import uuid

# 1. Crear el servidor MCP
mcp_server = Server("estudiante-ai-server")


# 2.0 Definir el Recurso Template
@mcp_server.list_resource_templates()
async def list_resource_templates() -> list[types.ResourceTemplate]:
    return [
        types.ResourceTemplate(
            uriTemplate="students://{student_id}/courses",
            name="Cursos del Estudiante",
            description="Recupera la lista de cursos para un ID de estudiante específico",
            mimeType="application/json",
        )
    ]


# 2.1 Definir el Recurso (Lista de Cursos)
@mcp_server.list_resources()
async def list_resources() -> list[types.Resource]:
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
    uri_str = str(uri)

    # El protocolo MCP asocia automáticamente la URI solicitada
    if uri_str.startswith("students://") and uri_str.endswith("/courses"):
        # Extraemos el ID dinámicamente
        student_id = uri_str.replace("students://", "").replace("/courses", "")

        # Pasamos el student_id (aunque fetch_courses aún devuelva lo mismo)
        courses_data = fetch_courses(student_id)

        current_week = courses_data[0]["current_week"] if courses_data else "1"
        current_date = datetime.now().strftime("%d/%m/%Y")

        result = {
            "student_id": student_id,  # Lo incluimos en la respuesta para confirmar
            "current_week": current_week,
            "current_date": current_date,
            "courses": [
                {"course_name": c["course_name"], "course_code": c["course_code"]}
                for c in courses_data
            ],
        }

        return json.dumps(result, ensure_ascii=False, indent=2)

    raise ValueError("Recurso no encontrado")


# 3. Definir la Herramienta
@mcp_server.list_tools()
async def list_tools() -> list[types.Tool]:
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
        )
    ]


@mcp_server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name == "get_filtered_courses":
        course_code = arguments.get("course_code")
        student_id = arguments.get("student_id")
        week = arguments.get("week")

        courses_data = fetch_courses(student_id)

        # Filter by course_code if provided
        if course_code:
            courses_data = [
                course
                for course in courses_data
                if course["course_code"] == course_code
            ]

        # Build result
        result = {
            "current_week": courses_data[0]["current_week"] if courses_data else "1",
            "current_date": datetime.now().strftime("%d/%m/%Y"),
            "courses": [],
        }

        # Process each course
        for course in courses_data:
            course_info = {
                "course_name": course["course_name"],
                "course_code": course["course_code"],
                "term_code": course["term_code"],
                "start_date": course["start_date"],
                "current_week": course["current_week"],
            }

            # If week is specified, include only assignments for that week
            if week:
                week_assignments = course.get("week_assignments", {}).get(week, [])
                course_info["assignments"] = week_assignments
                course_info["filtered_week"] = week
            else:
                # Include all week assignments
                course_info["week_assignments"] = course.get("week_assignments", {})

            result["courses"].append(course_info)

        return [
            types.TextContent(
                type="text", text=json.dumps(result, ensure_ascii=False, indent=2)
            )
        ]
    
    if name == "build_ics_file":
        student_id = arguments.get("student_id")
        course_code = arguments.get("course_code")
        week = arguments.get("week")

        courses_data = fetch_courses(student_id)

        # Filter courses by course_code if provided
        if course_code:
            courses_data = [
                course
                for course in courses_data
                if course["course_code"] == course_code
            ]

        # Collect assignments based on the week filter
        all_assignments = []
        for course in courses_data:
            if week:
                week_assignments = course.get("week_assignments", {}).get(week, [])
                all_assignments.extend(
                    [(assignment, course["course_code"]) for assignment in week_assignments]
                )
            else:
                for week_assignments in course.get("week_assignments", {}).values():
                    all_assignments.extend(
                        [(assignment, course["course_code"]) for assignment in week_assignments]
                    )

        if not all_assignments:
            return [
                types.TextContent(
                    type="text",
                    text="No assignments found for the specified filters."
                )
            ]

        cal = Calendar()

        for assignment, course_code_item in all_assignments:
            event = Event()

            summary = f"{course_code_item}: {assignment['title']}"
            description = assignment.get("instructions", "No description provided.")

            event.add("summary", summary)
            event.add("description", description)

            # Parse the due date
            due_date_str = assignment["due_date"]
            due_datetime_utc = datetime.strptime(
                due_date_str, "%Y-%m-%dT%H:%M:%SZ"
            ).replace(tzinfo=pytz.utc)

            # Properly format for an all-day event
            all_day_date = due_datetime_utc.date()

            event.add("uid", str(uuid.uuid4()))
            event.add("dtstamp", datetime.now(pytz.utc))
            event.add("dtstart", all_day_date)
            event.add("dtend", all_day_date + timedelta(days=1))
            event.add("status", "CONFIRMED")
            event.add("priority", 5)

            # Cross-platform all-day event indicators
            event["X-MICROSOFT-CDO-ALLDAYEVENT"] = "TRUE"
            event["X-APPLE-TRAVEL-ADVISORY-BEHAVIOR"] = "AUTOMATIC"
            event["TRANSP"] = "TRANSPARENT"

            event.add("categories", [course_code_item, "Assignment"])

            cal.add_component(event)

        # Generate ICS file content
        ics_data = cal.to_ical().decode("utf-8")

        return [
            types.TextContent(
                type="text",
                text=ics_data
            )
        ]

    raise ValueError(f"Herramienta desconocida: {name}")


# 4. Integrar con FastAPI para que Vercel lo pueda servir
app = FastAPI()
transport = SseServerTransport("/messages")


@app.get("/sse")
async def handle_sse(request: Request):
    async with transport.connect_sse(request.scope, request.receive, request._send) as (
        read_stream,
        write_stream,
    ):
        await mcp_server.run(
            read_stream, write_stream, mcp_server.create_initialization_options()
        )


@app.post("/messages")
async def handle_messages(request: Request):
    await transport.handle_post_message(request.scope, request.receive, request._send)
    return {"status": "ok"}


def fetch_courses(student_id: str):
    with open("api/example_data.json", "r", encoding="utf-8") as f:
        courses_data = json.load(f)
    return courses_data

# STDIO Entry Point for MCP Inspector
async def main():
    # Import standard IO transport inside the main loop
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await mcp_server.run(
            read_stream, write_stream, mcp_server.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
