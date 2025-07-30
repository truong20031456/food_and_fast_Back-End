"""
Validation Utilities - Data validation and sanitization functions.
"""

import re
from datetime import datetime, timedelta
from typing import Optional, Tuple


def validate_date_format(date_str: str) -> bool:
    """
    Validate date string format (YYYY-MM-DD).
    
    Args:
        date_str: Date string to validate
    
    Returns:
        True if valid, False otherwise
    """
    if not date_str:
        return False
    
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def validate_date_range(start_date: str, end_date: str) -> Tuple[bool, str]:
    """
    Validate date range (start_date <= end_date).
    
    Args:
        start_date: Start date string
        end_date: End date string
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not validate_date_format(start_date):
        return False, "Invalid start date format. Use YYYY-MM-DD"
    
    if not validate_date_format(end_date):
        return False, "Invalid end date format. Use YYYY-MM-DD"
    
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    
    if start > end:
        return False, "Start date cannot be after end date"
    
    # Check if date range is not too large (e.g., max 2 years)
    if (end - start).days > 730:
        return False, "Date range cannot exceed 2 years"
    
    return True, ""


def validate_period(period: str) -> bool:
    """
    Validate period parameter.
    
    Args:
        period: Period string to validate
    
    Returns:
        True if valid, False otherwise
    """
    valid_periods = ["daily", "weekly", "monthly", "yearly"]
    return period.lower() in valid_periods


def validate_limit(limit: int, max_limit: int = 100) -> bool:
    """
    Validate limit parameter.
    
    Args:
        limit: Limit value to validate
        max_limit: Maximum allowed limit
    
    Returns:
        True if valid, False otherwise
    """
    return isinstance(limit, int) and 1 <= limit <= max_limit


def sanitize_string(input_str: str) -> str:
    """
    Sanitize string input.
    
    Args:
        input_str: Input string to sanitize
    
    Returns:
        Sanitized string
    """
    if not input_str:
        return ""
    
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\']', '', input_str)
    return sanitized.strip()


def validate_email(email: str) -> bool:
    """
    Validate email format.
    
    Args:
        email: Email string to validate
    
    Returns:
        True if valid, False otherwise
    """
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def get_default_date_range(days: int = 30) -> Tuple[str, str]:
    """
    Get default date range for the last N days.
    
    Args:
        days: Number of days to look back
    
    Returns:
        Tuple of (start_date, end_date) in YYYY-MM-DD format
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")