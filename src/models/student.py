"""Student-related data models"""
from typing import List, Dict, Optional
from pydantic import BaseModel


class StudentResponse(BaseModel):
    """Response model for student course information"""
    student_id: Optional[str] = None
    current_week: str
    current_date: str
    courses: List[Dict]
