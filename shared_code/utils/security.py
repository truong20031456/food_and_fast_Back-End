"""
Security Configuration and Hardening
Provides security utilities and configurations for all services
"""

import os
import secrets
import hashlib
import hmac
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

from shared_code.utils.logging import get_logger

logger = get_logger(__name__)


class SecurityManager:
    """Central security manager for the platform."""

    def __init__(self):
        self.encryption_key = self._get_or_generate_key()
        self.fernet = Fernet(self.encryption_key)
        self.rate_limits = {}
        self.blocked_ips = set()

    def _get_or_generate_key(self) -> bytes:
        """Get existing encryption key or generate a new one."""
        key_file = "security.key"

        if os.path.exists(key_file):
            with open(key_file, "rb") as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, "wb") as f:
                f.write(key)
            logger.info("Generated new encryption key")
            return key

    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data."""
        try:
            encrypted = self.fernet.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            logger.error(f"Encryption error: {str(e)}")
            raise

    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data."""
        try:
            decoded = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = self.fernet.decrypt(decoded)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Decryption error: {str(e)}")
            raise

    def generate_secure_token(self, length: int = 32) -> str:
        """Generate cryptographically secure random token."""
        return secrets.token_urlsafe(length)

    def hash_password(
        self, password: str, salt: Optional[str] = None
    ) -> Dict[str, str]:
        """Hash password with salt using PBKDF2."""
        if salt is None:
            salt = secrets.token_hex(16)

        # Convert to bytes
        password_bytes = password.encode("utf-8")
        salt_bytes = salt.encode("utf-8")

        # Create PBKDF2 instance
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt_bytes,
            iterations=100000,  # OWASP recommended minimum
        )

        # Generate hash
        key = kdf.derive(password_bytes)
        hashed = base64.urlsafe_b64encode(key).decode()

        return {"hash": hashed, "salt": salt}

    def verify_password(self, password: str, hashed: str, salt: str) -> bool:
        """Verify password against hash."""
        try:
            password_hash = self.hash_password(password, salt)
            return hmac.compare_digest(password_hash["hash"], hashed)
        except Exception as e:
            logger.error(f"Password verification error: {str(e)}")
            return False

    def check_rate_limit(
        self, identifier: str, max_requests: int = 100, window_minutes: int = 60
    ) -> bool:
        """
        Check if request is within rate limits.

        Args:
            identifier: Unique identifier (IP, user_id, etc.)
            max_requests: Maximum requests allowed
            window_minutes: Time window in minutes

        Returns:
            True if within limits, False if exceeded
        """
        now = datetime.now()
        window_start = now - timedelta(minutes=window_minutes)

        # Clean old entries
        if identifier in self.rate_limits:
            self.rate_limits[identifier] = [
                timestamp
                for timestamp in self.rate_limits[identifier]
                if timestamp > window_start
            ]
        else:
            self.rate_limits[identifier] = []

        # Check current count
        current_count = len(self.rate_limits[identifier])

        if current_count >= max_requests:
            logger.warning(
                f"Rate limit exceeded for {identifier}: {current_count}/{max_requests}"
            )
            return False

        # Add current request
        self.rate_limits[identifier].append(now)
        return True

    def is_ip_blocked(self, ip_address: str) -> bool:
        """Check if IP address is blocked."""
        return ip_address in self.blocked_ips

    def block_ip(self, ip_address: str, reason: str = "Security violation"):
        """Block an IP address."""
        self.blocked_ips.add(ip_address)
        logger.warning(f"Blocked IP {ip_address}: {reason}")

    def validate_input(self, input_data: Any, validation_type: str) -> Dict[str, Any]:
        """
        Validate input data against common security threats.

        Args:
            input_data: Data to validate
            validation_type: Type of validation (sql_injection, xss, etc.)

        Returns:
            Validation result with is_valid and issues
        """
        result = {"is_valid": True, "issues": []}

        if not isinstance(input_data, str):
            return result

        input_lower = input_data.lower()

        if validation_type == "sql_injection":
            sql_patterns = [
                "select",
                "insert",
                "update",
                "delete",
                "drop",
                "union",
                "exec",
                "execute",
                "script",
                "javascript:",
                "vbscript:",
                "--",
                "/*",
                "*/",
                "@@",
                "char(",
                "varchar(",
                "nchar(",
                "nvarchar(",
                "alter",
                "create",
                "truncate",
            ]

            for pattern in sql_patterns:
                if pattern in input_lower:
                    result["is_valid"] = False
                    result["issues"].append(f"Potential SQL injection: {pattern}")

        elif validation_type == "xss":
            xss_patterns = [
                "<script",
                "</script>",
                "javascript:",
                "vbscript:",
                "onload=",
                "onerror=",
                "onclick=",
                "onmouseover=",
                "eval(",
                "expression(",
                "url(",
                "data:",
            ]

            for pattern in xss_patterns:
                if pattern in input_lower:
                    result["is_valid"] = False
                    result["issues"].append(f"Potential XSS: {pattern}")

        elif validation_type == "path_traversal":
            path_patterns = ["../", "..\\", "%2e%2e", "%2f", "%5c"]

            for pattern in path_patterns:
                if pattern in input_lower:
                    result["is_valid"] = False
                    result["issues"].append(f"Potential path traversal: {pattern}")

        return result

    def sanitize_input(self, input_data: str) -> str:
        """Sanitize input data."""
        import html
        import re

        # HTML encode
        sanitized = html.escape(input_data)

        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>"\']', "", sanitized)

        # Limit length
        sanitized = sanitized[:1000]

        return sanitized

    def generate_csrf_token(self, session_id: str) -> str:
        """Generate CSRF token for session."""
        timestamp = str(int(datetime.now().timestamp()))
        data = f"{session_id}:{timestamp}"

        # Create HMAC
        secret_key = os.getenv("CSRF_SECRET_KEY", "default-csrf-key")
        signature = hmac.new(
            secret_key.encode(), data.encode(), hashlib.sha256
        ).hexdigest()

        token = f"{data}:{signature}"
        return base64.urlsafe_b64encode(token.encode()).decode()

    def verify_csrf_token(
        self, token: str, session_id: str, max_age_hours: int = 24
    ) -> bool:
        """Verify CSRF token."""
        try:
            # Decode token
            decoded = base64.urlsafe_b64decode(token.encode()).decode()
            parts = decoded.split(":")

            if len(parts) != 3:
                return False

            received_session, timestamp, signature = parts

            # Verify session ID
            if received_session != session_id:
                return False

            # Check age
            token_time = datetime.fromtimestamp(int(timestamp))
            if datetime.now() - token_time > timedelta(hours=max_age_hours):
                return False

            # Verify signature
            secret_key = os.getenv("CSRF_SECRET_KEY", "default-csrf-key")
            expected_signature = hmac.new(
                secret_key.encode(),
                f"{received_session}:{timestamp}".encode(),
                hashlib.sha256,
            ).hexdigest()

            return hmac.compare_digest(signature, expected_signature)

        except Exception as e:
            logger.error(f"CSRF token verification error: {str(e)}")
            return False


class SecurityHeaders:
    """Security headers for HTTP responses."""

    @staticmethod
    def get_security_headers() -> Dict[str, str]:
        """Get recommended security headers."""
        return {
            # Prevent clickjacking
            "X-Frame-Options": "DENY",
            # Prevent MIME type sniffing
            "X-Content-Type-Options": "nosniff",
            # XSS protection
            "X-XSS-Protection": "1; mode=block",
            # Referrer policy
            "Referrer-Policy": "strict-origin-when-cross-origin",
            # Content Security Policy
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self'; "
                "connect-src 'self'"
            ),
            # HSTS (HTTPS Strict Transport Security)
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            # Permissions policy
            "Permissions-Policy": (
                "geolocation=(), "
                "microphone=(), "
                "camera=(), "
                "payment=(), "
                "usb=(), "
                "magnetometer=(), "
                "gyroscope=(), "
                "speaker=(), "
                "vibrate=(), "
                "fullscreen=()"
            ),
        }


class SecurityAudit:
    """Security audit and logging utilities."""

    def __init__(self, service_name: str):
        self.service_name = service_name
        self.logger = get_logger(f"security.{service_name}")

    def log_security_event(
        self,
        event_type: str,
        details: Dict[str, Any],
        severity: str = "INFO",
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
    ):
        """Log security events for monitoring."""
        event_data = {
            "timestamp": datetime.now().isoformat(),
            "service": self.service_name,
            "event_type": event_type,
            "severity": severity,
            "user_id": user_id,
            "ip_address": ip_address,
            "details": details,
        }

        if severity == "CRITICAL":
            self.logger.critical(f"Security Event: {event_data}")
        elif severity == "WARNING":
            self.logger.warning(f"Security Event: {event_data}")
        else:
            self.logger.info(f"Security Event: {event_data}")

    def log_authentication_attempt(
        self,
        user_id: str,
        success: bool,
        ip_address: str,
        user_agent: Optional[str] = None,
    ):
        """Log authentication attempts."""
        self.log_security_event(
            event_type="authentication_attempt",
            details={"success": success, "user_agent": user_agent},
            severity="WARNING" if not success else "INFO",
            user_id=user_id,
            ip_address=ip_address,
        )

    def log_permission_denied(
        self, user_id: str, resource: str, action: str, ip_address: str
    ):
        """Log permission denied events."""
        self.log_security_event(
            event_type="permission_denied",
            details={"resource": resource, "action": action},
            severity="WARNING",
            user_id=user_id,
            ip_address=ip_address,
        )

    def log_suspicious_activity(
        self,
        activity_type: str,
        details: Dict[str, Any],
        ip_address: str,
        user_id: Optional[str] = None,
    ):
        """Log suspicious activities."""
        self.log_security_event(
            event_type="suspicious_activity",
            details={"activity_type": activity_type, **details},
            severity="CRITICAL",
            user_id=user_id,
            ip_address=ip_address,
        )


# Security configuration for different environments
SECURITY_CONFIG = {
    "development": {
        "enforce_https": False,
        "session_timeout_minutes": 480,  # 8 hours
        "max_login_attempts": 10,
        "lockout_duration_minutes": 5,
        "password_min_length": 8,
        "require_special_chars": False,
    },
    "staging": {
        "enforce_https": True,
        "session_timeout_minutes": 240,  # 4 hours
        "max_login_attempts": 5,
        "lockout_duration_minutes": 15,
        "password_min_length": 10,
        "require_special_chars": True,
    },
    "production": {
        "enforce_https": True,
        "session_timeout_minutes": 120,  # 2 hours
        "max_login_attempts": 3,
        "lockout_duration_minutes": 30,
        "password_min_length": 12,
        "require_special_chars": True,
    },
}


def get_security_config(environment: str = "development") -> Dict[str, Any]:
    """Get security configuration for environment."""
    return SECURITY_CONFIG.get(environment, SECURITY_CONFIG["development"])
