"""Course and Assignment data models"""
from typing import Dict, List, Optional
from pydantic import BaseModel


class Assignment(BaseModel):
    """Represents a course assignment"""
    title: str
    points_possible_decimal: float
    description: str
    submission_type: str
    due_on: str
    instructions: Optional[str] = None


class WeekAssignments(BaseModel):
    """Represents assignments organized by week"""
    week_assignments: Dict[str, List[Assignment]]


class Course(BaseModel):
    """Represents a student course"""
    course_name: str
    course_code: str
    term_code: str
    start_date: str
    current_week: str
    week_assignments: Dict[str, List[dict]]
