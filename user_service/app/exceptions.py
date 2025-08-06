"""Custom exceptions for the user service"""


class UserServiceException(Exception):
    """Base exception for user service"""

    pass


class UserNotFoundError(UserServiceException):
    """Raised when a user is not found"""

    pass


class DuplicateUserError(UserServiceException):
    """Raised when trying to create a user with existing email/username"""

    pass


class UserAuthorizationError(UserServiceException):
    """Raised when user is not authorized to perform an action"""

    pass


class DatabaseError(UserServiceException):
    """Raised when database operations fail"""

    pass


class CacheError(UserServiceException):
    """Raised when cache operations fail"""

    pass


class ValidationError(UserServiceException):
    """Raised when data validation fails"""

    pass


class AuthenticationError(UserServiceException):
    """Raised when authentication fails"""

    pass
