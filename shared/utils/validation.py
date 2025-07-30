"""
Common validation utilities
"""
import re
from typing import Optional, Any, List
from email_validator import validate_email, EmailNotValidError
from pydantic import BaseModel, validator
from datetime import datetime, date
import phonenumbers
from phonenumbers import NumberParseException
import logging

logger = logging.getLogger(__name__)


class ValidationUtils:
    """Common validation utilities"""
    
    # Regex patterns
    UUID_PATTERN = re.compile(
        r'^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$',
        re.IGNORECASE
    )
    
    USERNAME_PATTERN = re.compile(r'^[a-zA-Z0-9_]{3,20}$')
    PASSWORD_PATTERN = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$')
    SLUG_PATTERN = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
    
    @staticmethod
    def validate_email_address(email: str) -> tuple[bool, Optional[str]]:
        """
        Validate email address
        
        Returns:
            Tuple of (is_valid, normalized_email_or_error_message)
        """
        try:
            valid = validate_email(email)
            return True, valid.email
        except EmailNotValidError as e:
            return False, str(e)
    
    @staticmethod
    def validate_phone_number(phone: str, country_code: str = None) -> tuple[bool, Optional[str]]:
        """
        Validate phone number
        
        Args:
            phone: Phone number string
            country_code: Country code (e.g., 'US', 'VN')
            
        Returns:
            Tuple of (is_valid, formatted_number_or_error_message)
        """
        try:
            parsed = phonenumbers.parse(phone, country_code)
            if phonenumbers.is_valid_number(parsed):
                formatted = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
                return True, formatted
            else:
                return False, "Invalid phone number"
        except NumberParseException as e:
            return False, str(e)
    
    @staticmethod
    def validate_uuid(uuid_string: str) -> bool:
        """Validate UUID string format"""
        return bool(ValidationUtils.UUID_PATTERN.match(uuid_string))
    
    @staticmethod
    def validate_username(username: str) -> bool:
        """Validate username format"""
        return bool(ValidationUtils.USERNAME_PATTERN.match(username))
    
    @staticmethod
    def validate_password_strength(password: str) -> tuple[bool, List[str]]:
        """
        Validate password strength
        
        Returns:
            Tuple of (is_valid, list_of_requirements_not_met)
        """
        errors = []
        
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        
        if not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        if not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        if not re.search(r'\d', password):
            errors.append("Password must contain at least one digit")
        
        if not re.search(r'[@$!%*?&]', password):
            errors.append("Password must contain at least one special character (@$!%*?&)")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_slug(slug: str) -> bool:
        """Validate URL slug format"""
        return bool(ValidationUtils.SLUG_PATTERN.match(slug))
    
    @staticmethod
    def validate_positive_number(value: Any) -> bool:
        """Validate positive number"""
        try:
            num = float(value)
            return num > 0
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_date_range(start_date: date, end_date: date) -> bool:
        """Validate date range (start <= end)"""
        return start_date <= end_date
    
    @staticmethod
    def validate_datetime_range(start_dt: datetime, end_dt: datetime) -> bool:
        """Validate datetime range (start <= end)"""
        return start_dt <= end_dt
    
    @staticmethod
    def sanitize_string(value: str, max_length: Optional[int] = None) -> str:
        """Sanitize string input"""
        if not isinstance(value, str):
            return str(value)
        
        # Strip whitespace
        sanitized = value.strip()
        
        # Remove null bytes and control characters
        sanitized = ''.join(char for char in sanitized if ord(char) >= 32 or char in '\t\n\r')
        
        # Truncate if max_length specified
        if max_length and len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        return sanitized
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """Basic URL validation"""
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return bool(url_pattern.match(url))


# Pydantic validators

def email_validator(v: str) -> str:
    """Pydantic validator for email"""
    is_valid, result = ValidationUtils.validate_email_address(v)
    if not is_valid:
        raise ValueError(result)
    return result


def phone_validator(v: str) -> str:
    """Pydantic validator for phone number"""
    is_valid, result = ValidationUtils.validate_phone_number(v)
    if not is_valid:
        raise ValueError(result)
    return result


def password_validator(v: str) -> str:
    """Pydantic validator for password strength"""
    is_valid, errors = ValidationUtils.validate_password_strength(v)
    if not is_valid:
        raise ValueError("; ".join(errors))
    return v


def username_validator(v: str) -> str:
    """Pydantic validator for username"""
    if not ValidationUtils.validate_username(v):
        raise ValueError("Username must be 3-20 characters long and contain only letters, numbers, and underscores")
    return v


def uuid_validator(v: str) -> str:
    """Pydantic validator for UUID"""
    if not ValidationUtils.validate_uuid(v):
        raise ValueError("Invalid UUID format")
    return v


def positive_number_validator(v: float) -> float:
    """Pydantic validator for positive numbers"""
    if not ValidationUtils.validate_positive_number(v):
        raise ValueError("Value must be a positive number")
    return v


def url_validator(v: str) -> str:
    """Pydantic validator for URLs"""
    if not ValidationUtils.validate_url(v):
        raise ValueError("Invalid URL format")
    return v


def sanitize_string_validator(v: str) -> str:
    """Pydantic validator to sanitize strings"""
    return ValidationUtils.sanitize_string(v)


# Common validation schemas

class EmailStr(str):
    """String subclass for validated email addresses"""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            raise TypeError('string required')
        
        is_valid, result = ValidationUtils.validate_email_address(v)
        if not is_valid:
            raise ValueError(result)
        return cls(result)


class PhoneStr(str):
    """String subclass for validated phone numbers"""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            raise TypeError('string required')
        
        is_valid, result = ValidationUtils.validate_phone_number(v)
        if not is_valid:
            raise ValueError(result)
        return cls(result)


class UUIDStr(str):
    """String subclass for validated UUIDs"""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            raise TypeError('string required')
        
        if not ValidationUtils.validate_uuid(v):
            raise ValueError('Invalid UUID format')
        return cls(v)


# Validation mixins for Pydantic models

class EmailValidationMixin(BaseModel):
    """Mixin for email validation"""
    
    @validator('email', pre=True)
    def validate_email(cls, v):
        return email_validator(v)


class PhoneValidationMixin(BaseModel):
    """Mixin for phone validation"""
    
    @validator('phone', 'phone_number', pre=True)
    def validate_phone(cls, v):
        return phone_validator(v)


class PasswordValidationMixin(BaseModel):
    """Mixin for password validation"""
    
    @validator('password', pre=True)
    def validate_password(cls, v):
        return password_validator(v)


class StringSanitizationMixin(BaseModel):
    """Mixin for string sanitization"""
    
    @validator('*', pre=True)
    def sanitize_strings(cls, v):
        if isinstance(v, str):
            return ValidationUtils.sanitize_string(v)
        return v