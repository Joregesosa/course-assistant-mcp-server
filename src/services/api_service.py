from html import unescape
import logging
import re
from typing import Dict, List, Any
from src.config import COURSES_API_URL
import requests

class APIService:

    @staticmethod
    def clean_html(html_text: str) -> str:
        """
        Remove HTML tags and clean text to save tokens.

        Args:
            html_text: The HTML text to clean.

        Returns:
            Cleaned text without HTML tags.
        """
        if not html_text:
            return ""
        # Remove style and script tags
        clean = re.sub(r"<(style|script)[^>]*>.*?</\1>", "", html_text, flags=re.DOTALL)
        # Replace breaks and list items with line breaks/dashes
        clean = re.sub(r"<br\s*/?>", "\n", clean)
        clean = re.sub(r"<li>", "\n- ", clean)
        # Remove remaining HTML tags
        clean = re.sub(r"<[^>]+>", "", clean)
        # Decode HTML entities (e.g., &nbsp; to space) and clean extra spaces
        return unescape(clean).strip()

    @staticmethod
    def get_courses_from_api(student_id: str) -> List[Dict[str, Any]]:
        """
        Fetch and process course data for a specific user from the external API.

        This function retrieves course information including assignments, submissions,
        and course details, then processes and formats the data for easier consumption.

        Args:
            student_id: The unique identifier of the user.

        Returns:
            A list of dictionaries containing processed course information with:
            - name: Course name
            - code: Course code
            - current_week: Current week number
            - week_assignments: Dictionary of assignments organized by week
            Each assignment includes title, points, due date, type, instructions,
            status, and grade (if applicable).

        Note:
            Returns an empty list if the API call fails or encounters an error.
        """
        try:
            response = requests.post(
                url=COURSES_API_URL,
                json={"user_id": student_id}
            )
            print("API_URL:", COURSES_API_URL)
            print("Student:", student_id)
            print("Response", response.ok)
            if not response.ok:
                return []

            data = response.json()
            current_courses = data.get("current_courses", [])
            guids = data.get("guids", [])
            week_assignments = data.get("week_assignments", [])
            submissions = data.get("submissions", [])
            
            # Quick lookup maps
            guid_map = {g["canvas_sis_id"]: g for g in guids}
            submission_map = {}
            for s in submissions:
                submission_map.setdefault(s["canvas_assignment_id"], []).append(s)

            output_courses = []

            for course in current_courses:
                course_info = guid_map.get(course["canvas_sis_id"], {})
                course_id = course_info.get("canvas_course_id")

                # Use current_week directly from guids
                processed_course = {
                    "course_name": course.get("course_name", "Unknown Course"),
                    "course_code": course.get("course_code", "Unknown Code"),
                    "term_code": course.get("term_code", "Unknown Term"),
                    "start_date": course.get("start_date", "Unknown Start Date"),
                    "current_week": int(course_info.get("current_week", 0)),
                    "week_assignments": {},
                }

                # Filter and clean assignments
                for assignment in week_assignments:
                    if assignment["canvas_course_id"] == course_id:
                        week = str(assignment["due_week"])

                        clean_assignment = {
                            "title": assignment["title"],
                            "possible_score": assignment["points_possible_decimal"],
                            "due_on": f"{assignment['due_on']}",
                            "type": assignment["submission_type"],
                            "instructions": APIService.clean_html(
                                assignment.get("description", "")
                            ),
                        }

                        # Submission status (simplified)
                        subs = submission_map.get(
                            assignment["canvas_assignment_id"], []
                        )
                        if subs:
                            clean_assignment["status"] = "Submitted"
                            if subs[0].get("score") is not None:
                                clean_assignment["grade"] = subs[0]["score"]
                        else:
                            clean_assignment["status"] = "Pending"

                        processed_course["week_assignments"].setdefault(
                            week, []
                        ).append(clean_assignment)

                output_courses.append(processed_course)

            return output_courses
        except Exception as e:
            logging.error(f"Error fetching courses from API: {str(e)}")
            return []
