"""
Validation Utilities - Data validation and sanitization functions for notifications.
"""

import re
from typing import Optional, Tuple


def validate_phone_number(phone: str) -> bool:
    """
    Validate phone number format.

    Args:
        phone: Phone number to validate

    Returns:
        True if valid, False otherwise
    """
    if not phone:
        return False

    # Remove all non-digit characters
    digits_only = re.sub(r"\D", "", phone)

    # Check if it's a valid length (10-15 digits)
    if len(digits_only) < 10 or len(digits_only) > 15:
        return False

    return True


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

    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def validate_sms_message(message: str, max_length: int = 160) -> Tuple[bool, str]:
    """
    Validate SMS message.

    Args:
        message: Message to validate
        max_length: Maximum allowed length

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not message:
        return False, "Message cannot be empty"

    if len(message) > max_length:
        return False, f"Message exceeds maximum length of {max_length} characters"

    return True, ""


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
    sanitized = re.sub(r'[<>"\']', "", input_str)
    return sanitized.strip()


def validate_template_name(template: str) -> bool:
    """
    Validate template name format.

    Args:
        template: Template name to validate

    Returns:
        True if valid, False otherwise
    """
    if not template:
        return False

    # Template names should be alphanumeric with underscores and hyphens
    pattern = r"^[a-zA-Z0-9_-]+$"
    return re.match(pattern, template) is not None


def validate_user_id(user_id: int) -> bool:
    """
    Validate user ID.

    Args:
        user_id: User ID to validate

    Returns:
        True if valid, False otherwise
    """
    return isinstance(user_id, int) and user_id > 0


def validate_notification_data(data: dict) -> Tuple[bool, str]:
    """
    Validate notification data.

    Args:
        data: Notification data to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(data, dict):
        return False, "Data must be a dictionary"

    # Check for required fields if needed
    # Add specific validation logic here

    return True, ""


def format_phone_number(phone: str) -> str:
    """
    Format phone number to standard format.

    Args:
        phone: Phone number to format

    Returns:
        Formatted phone number
    """
    if not phone:
        return ""

    # Remove all non-digit characters
    digits_only = re.sub(r"\D", "", phone)

    # Add country code if missing (assuming Vietnam +84)
    if len(digits_only) == 10 and digits_only.startswith("0"):
        digits_only = "84" + digits_only[1:]

    return f"+{digits_only}" if digits_only else ""


def truncate_message(message: str, max_length: int = 160) -> str:
    """
    Truncate message to fit SMS limits.

    Args:
        message: Message to truncate
        max_length: Maximum allowed length

    Returns:
        Truncated message
    """
    if len(message) <= max_length:
        return message

    # Truncate and add ellipsis
    return message[: max_length - 3] + "..."
