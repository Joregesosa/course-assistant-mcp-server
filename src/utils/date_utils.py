"""Date and time utility functions"""
from datetime import datetime
import pytz


def get_current_date_formatted(format_str: str = "%d/%m/%Y") -> str:
    """
    Get current date formatted as string
    
    Args:
        format_str: Date format string
        
    Returns:
        Formatted date string
    """
    return datetime.now().strftime(format_str)


def parse_utc_datetime(date_str: str) -> datetime:
    """
    Parse UTC datetime string
    
    Args:
        date_str: Date string in format '%Y-%m-%dT%H:%M:%SZ'
        
    Returns:
        datetime object with UTC timezone
    """
    return datetime.strptime(
        date_str, "%Y-%m-%dT%H:%M:%SZ"
    ).replace(tzinfo=pytz.utc)
