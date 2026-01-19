"""Service for calendar and ICS file generation"""
from typing import List, Dict, Tuple
from datetime import datetime, timedelta
from icalendar import Calendar, Event
import pytz
import uuid


class CalendarService:
    """Handles ICS calendar file generation"""

    @staticmethod
    def collect_assignments(
        courses_data: List[Dict],
        week: str = None
    ) -> List[Tuple[Dict, str]]:
        """
        Collect assignments from courses
        
        Args:
            courses_data: List of course dictionaries
            week: Optional week filter
            
        Returns:
            List of tuples (assignment, course_code)
        """
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
        
        return all_assignments

    @staticmethod
    def create_assignment_event(assignment: Dict, course_code: str) -> Event:
        """
        Create a calendar event for an assignment
        
        Args:
            assignment: Assignment dictionary
            course_code: Course code string
            
        Returns:
            icalendar Event object
        """
        event = Event()

        summary = f"{course_code}: {assignment['title']}"
        description = assignment.get("instructions", "No description provided.")

        event.add("summary", summary)
        event.add("description", description)

        # Parse the due date
        due_date_str = assignment["due_on"]
        due_datetime_utc = datetime.strptime(
            due_date_str, "%Y-%m-%dT%H:%M:%SZ"
        ).replace(tzinfo=pytz.utc)

        # Format for an all-day event
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

        event.add("categories", [course_code, "Assignment"])

        return event

    @staticmethod
    def build_ics_calendar(
        courses_data: List[Dict],
        course_code: str = None,
        week: str = None
    ) -> str:
        """
        Build an ICS calendar file from courses and assignments
        
        Args:
            courses_data: List of course dictionaries
            course_code: Optional course code filter
            week: Optional week filter
            
        Returns:
            ICS file content as string
        """
        # Filter courses by course_code if provided
        if course_code:
            courses_data = [
                course
                for course in courses_data
                if course["course_code"] == course_code
            ]

        # Collect assignments
        all_assignments = CalendarService.collect_assignments(courses_data, week)

        if not all_assignments:
            return "No assignments found for the specified filters."

        cal = Calendar()

        for assignment, course_code_item in all_assignments:
            event = CalendarService.create_assignment_event(assignment, course_code_item)
            cal.add_component(event)

        # Generate ICS file content
        ics_data = cal.to_ical().decode("utf-8")
        return ics_data
