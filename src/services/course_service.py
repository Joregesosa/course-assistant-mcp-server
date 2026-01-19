"""Service for course-related business logic"""

import json
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
from src.services.api_service import APIService
from src.services.redis_cache_service import StudentCache


class CourseService:
    """Handles course data retrieval and filtering"""

    def __init__(self, cache_expiration: int = 1800):
        """
        Initialize the CourseService with a Redis cache.

        Args:
            cache_expiration: Cache expiration time in seconds (default 30 minutes).
        """
        self.cache = StudentCache(expiration_time=cache_expiration)
        logging.info(
            f"CourseService initialized with cache expiration: {cache_expiration}s"
        )

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
        return [course for course in courses if course["course_code"] == course_code]

    @staticmethod
    def format_course_response(
        courses_data: List[Dict],
        student_id: Optional[str] = None,
        week: Optional[str] = None,
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
                "course_name": course.get("course_name", "Unknown Course"),
                "course_code": course.get("course_code", "Unknown Code"),
                "term_code": course.get("term_code", "Unknown Term"),
                "start_date": course.get("start_date", "Unknown Start Date"),
                "current_week": course.get("current_week", "1"),
            }

            if week:
                week_assignments = course.get("week_assignments", {}).get(week, [])
                course_info["assignments"] = week_assignments
                course_info["filtered_week"] = week
            else:
                course_info["week_assignments"] = course.get("week_assignments", {})

            result["courses"].append(course_info)

        return result

    def fetch_courses(self, student_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve course data for a user, using cache when available.

        This method implements the following flow:
        1. Check if data exists in Redis cache
        2. If cached data exists, deserialize and return it
        3. If not cached, fetch from API
        4. Store the API response in cache

        Args:
            user_id: The unique identifier of the user.

        Returns:
            A list of course dictionaries with detailed information

        Raises:
            ValueError: If user_id is empty or invalid.
            Exception: If both Redis and API retrieval fail.
        """
        if not student_id or not student_id.strip():
            raise ValueError("student_id cannot be empty")

        student_id = student_id.strip()

        # Try to get data from Redis cache
        try:
            logging.info(f"Checking cache existence for user {student_id}")
            if self.cache.exists(student_id):
                courses = self.cache.get(student_id)
                json_courses = (
                    json.loads(courses) if isinstance(courses, str) else courses
                )

                logging.info(f"Returning cached courses for user {student_id}")
                return json_courses

            logging.info(f"No cache found for user {student_id}, fetching from API")
            courses = APIService.get_courses_from_api(student_id)
            if courses:
                self.cache.set(student_id, json.dumps(courses))
                logging.info(f"Cached courses for user {student_id}")

            logging.info(f"Returning courses from API for user {student_id}")
            return courses

        except Exception as e:
            logging.error(f"Error retrieving from cache for user {student_id}: {e}")
            return []  # Return an empty list in case of an error

    def check_cache_exists(self, user_id: str) -> bool:
        """
        Check if cached data exists for a user without retrieving it.

        Args:
            user_id: The unique identifier of the user.

        Returns:
            True if cached data exists, False otherwise.
        """
        try:
            return self.cache.exists(user_id)
        except Exception as e:
            logging.error(f"Error checking cache existence for user {user_id}: {e}")
            return False

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
