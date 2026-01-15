"""Service for course-related business logic"""
import json
from typing import List, Dict, Optional
from datetime import datetime
from src.config import DATA_FILE_PATH


class CourseService:
    """Handles course data retrieval and filtering"""

    @staticmethod
    def fetch_courses(student_id: str) -> List[Dict]:
        """
        Fetch courses for a specific student
        
        Args:
            student_id: The student identifier
            
        Returns:
            List of course dictionaries
        """
        with open(DATA_FILE_PATH, "r", encoding="utf-8") as f:
            courses_data = json.load(f)
        return courses_data

    @staticmethod
    def filter_by_course_code(courses: List[Dict], course_code: str) -> List[Dict]:
        """
        Filter courses by course code
        
        Args:
            courses: List of course dictionaries
            course_code: Course code to filter by
            
        Returns:
            Filtered list of courses
        """
        return [
            course
            for course in courses
            if course["course_code"] == course_code
        ]

    @staticmethod
    def format_course_response(
        courses_data: List[Dict],
        student_id: Optional[str] = None,
        week: Optional[str] = None
    ) -> Dict:
        """
        Format courses into a structured response
        
        Args:
            courses_data: List of course dictionaries
            student_id: Optional student identifier
            week: Optional week filter
            
        Returns:
            Formatted response dictionary
        """
        result = {
            "current_week": courses_data[0]["current_week"] if courses_data else "1",
            "current_date": datetime.now().strftime("%d/%m/%Y"),
            "courses": [],
        }

        if student_id:
            result["student_id"] = student_id

        for course in courses_data:
            course_info = {
                "course_name": course["course_name"],
                "course_code": course["course_code"],
                "term_code": course["term_code"],
                "start_date": course["start_date"],
                "current_week": course["current_week"],
            }

            if week:
                week_assignments = course.get("week_assignments", {}).get(week, [])
                course_info["assignments"] = week_assignments
                course_info["filtered_week"] = week
            else:
                course_info["week_assignments"] = course.get("week_assignments", {})

            result["courses"].append(course_info)

        return result

    @staticmethod
    def get_basic_course_info(courses_data: List[Dict]) -> List[Dict]:
        """
        Get basic course information (name and code only)
        
        Args:
            courses_data: List of course dictionaries
            
        Returns:
            List of basic course info
        """
        return [
            {"course_name": c["course_name"], "course_code": c["course_code"]}
            for c in courses_data
        ]
