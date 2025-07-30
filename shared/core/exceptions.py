"""
Custom exceptions for all services
"""
from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class BaseServiceException(Exception):
    """Base exception for all service-specific exceptions"""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(BaseServiceException):
    """Raised when validation fails"""
    pass


class NotFoundError(BaseServiceException):
    """Raised when a resource is not found"""
    pass


class ConflictError(BaseServiceException):
    """Raised when there's a conflict (e.g., duplicate resource)"""
    pass


class UnauthorizedError(BaseServiceException):
    """Raised when authentication fails"""
    pass


class ForbiddenError(BaseServiceException):
    """Raised when authorization fails"""
    pass


class ExternalServiceError(BaseServiceException):
    """Raised when external service call fails"""
    pass


class DatabaseError(BaseServiceException):
    """Raised when database operation fails"""
    pass


class CacheError(BaseServiceException):
    """Raised when cache operation fails"""
    pass


# HTTP Exception mappings
def create_http_exception(
    exception: BaseServiceException,
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
) -> HTTPException:
    """Convert service exception to HTTP exception"""
    
    detail = {
        "message": exception.message,
        "error_code": exception.error_code,
        "details": exception.details
    }
    
    return HTTPException(
        status_code=status_code,
        detail=detail
    )


def validation_exception(
    message: str,
    error_code: str = "VALIDATION_ERROR",
    details: Optional[Dict[str, Any]] = None
) -> HTTPException:
    """Create validation HTTP exception"""
    return create_http_exception(
        ValidationError(message, error_code, details),
        status.HTTP_422_UNPROCESSABLE_ENTITY
    )


def not_found_exception(
    message: str,
    error_code: str = "RESOURCE_NOT_FOUND",
    details: Optional[Dict[str, Any]] = None
) -> HTTPException:
    """Create not found HTTP exception"""
    return create_http_exception(
        NotFoundError(message, error_code, details),
        status.HTTP_404_NOT_FOUND
    )


def conflict_exception(
    message: str,
    error_code: str = "RESOURCE_CONFLICT",
    details: Optional[Dict[str, Any]] = None
) -> HTTPException:
    """Create conflict HTTP exception"""
    return create_http_exception(
        ConflictError(message, error_code, details),
        status.HTTP_409_CONFLICT
    )


def unauthorized_exception(
    message: str = "Authentication required",
    error_code: str = "UNAUTHORIZED",
    details: Optional[Dict[str, Any]] = None
) -> HTTPException:
    """Create unauthorized HTTP exception"""
    return create_http_exception(
        UnauthorizedError(message, error_code, details),
        status.HTTP_401_UNAUTHORIZED
    )


def forbidden_exception(
    message: str = "Access forbidden",
    error_code: str = "FORBIDDEN",
    details: Optional[Dict[str, Any]] = None
) -> HTTPException:
    """Create forbidden HTTP exception"""
    return create_http_exception(
        ForbiddenError(message, error_code, details),
        status.HTTP_403_FORBIDDEN
    )