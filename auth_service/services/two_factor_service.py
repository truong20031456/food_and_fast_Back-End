"""
Two-Factor Authentication Service
Provides TOTP-based 2FA functionality
"""

import pyotp
import qrcode
import io
import base64
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from shared_code.utils.redis import get_redis_manager
from shared_code.utils.logging import get_logger

logger = get_logger(__name__)


class TwoFactorAuthService:
    """Service for handling Two-Factor Authentication."""

    def __init__(self, redis_manager=None):
        self.redis = redis_manager or get_redis_manager()
        self.app_name = "Food & Fast"
        self.backup_codes_count = 10

    def generate_secret(self, user_email: str) -> str:
        """
        Generate a new TOTP secret for a user.

        Args:
            user_email: User's email address

        Returns:
            Base32-encoded secret string
        """
        try:
            secret = pyotp.random_base32()
            logger.info(f"Generated 2FA secret for user: {user_email}")
            return secret

        except Exception as e:
            logger.error(f"Error generating 2FA secret: {str(e)}")
            raise

    def generate_qr_code(self, user_email: str, secret: str) -> str:
        """
        Generate QR code for 2FA setup.

        Args:
            user_email: User's email address
            secret: TOTP secret

        Returns:
            Base64-encoded QR code image
        """
        try:
            # Create TOTP URI
            totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
                name=user_email, issuer_name=self.app_name
            )

            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(totp_uri)
            qr.make(fit=True)

            # Create image
            img = qr.make_image(fill_color="black", back_color="white")

            # Convert to base64
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            img_str = base64.b64encode(buffer.getvalue()).decode()

            logger.info(f"Generated QR code for user: {user_email}")
            return img_str

        except Exception as e:
            logger.error(f"Error generating QR code: {str(e)}")
            raise

    def verify_token(self, secret: str, token: str, window: int = 1) -> bool:
        """
        Verify a TOTP token.

        Args:
            secret: User's TOTP secret
            token: Token to verify
            window: Time window for verification (±30 seconds * window)

        Returns:
            True if token is valid
        """
        try:
            totp = pyotp.TOTP(secret)
            is_valid = totp.verify(token, valid_window=window)

            if is_valid:
                logger.info("2FA token verification successful")
            else:
                logger.warning("2FA token verification failed")

            return is_valid

        except Exception as e:
            logger.error(f"Error verifying 2FA token: {str(e)}")
            return False

    async def enable_2fa(
        self, user_id: str, user_email: str, token: str
    ) -> Dict[str, Any]:
        """
        Enable 2FA for a user after token verification.

        Args:
            user_id: User ID
            user_email: User's email
            token: Verification token

        Returns:
            Dict containing setup result and backup codes
        """
        try:
            # Get the secret from temporary storage
            temp_secret_key = f"2fa_temp_secret:{user_id}"
            secret = await self.redis.get(temp_secret_key)

            if not secret:
                return {
                    "success": False,
                    "message": "2FA setup session expired. Please start again.",
                }

            # Verify the token
            if not self.verify_token(secret, token):
                return {
                    "success": False,
                    "message": "Invalid verification code. Please try again.",
                }

            # Generate backup codes
            backup_codes = self.generate_backup_codes()

            # Store 2FA data permanently
            user_2fa_key = f"2fa_user:{user_id}"
            await self.redis.hset(
                user_2fa_key,
                {
                    "secret": secret,
                    "enabled": "true",
                    "enabled_at": datetime.now().isoformat(),
                    "backup_codes": ",".join(backup_codes),
                },
            )

            # Remove temporary secret
            await self.redis.delete(temp_secret_key)

            logger.info(f"2FA enabled successfully for user: {user_id}")

            return {
                "success": True,
                "message": "2FA has been enabled successfully",
                "backup_codes": backup_codes,
            }

        except Exception as e:
            logger.error(f"Error enabling 2FA: {str(e)}")
            return {"success": False, "message": "An error occurred while enabling 2FA"}

    async def disable_2fa(
        self, user_id: str, password: str, token: str
    ) -> Dict[str, Any]:
        """
        Disable 2FA for a user.

        Args:
            user_id: User ID
            password: User's password for verification
            token: 2FA token for verification

        Returns:
            Dict containing operation result
        """
        try:
            # Get user's 2FA data
            user_2fa_key = f"2fa_user:{user_id}"
            user_2fa_data = await self.redis.hgetall(user_2fa_key)

            if not user_2fa_data or user_2fa_data.get("enabled") != "true":
                return {"success": False, "message": "2FA is not enabled for this user"}

            # Verify token
            secret = user_2fa_data.get("secret")
            if not self.verify_token(secret, token):
                return {"success": False, "message": "Invalid 2FA code"}

            # TODO: Verify password (should be done by calling auth service)

            # Disable 2FA
            await self.redis.delete(user_2fa_key)

            logger.info(f"2FA disabled for user: {user_id}")

            return {"success": True, "message": "2FA has been disabled successfully"}

        except Exception as e:
            logger.error(f"Error disabling 2FA: {str(e)}")
            return {
                "success": False,
                "message": "An error occurred while disabling 2FA",
            }

    async def verify_2fa_login(self, user_id: str, token: str) -> bool:
        """
        Verify 2FA token during login.

        Args:
            user_id: User ID
            token: 2FA token

        Returns:
            True if verification successful
        """
        try:
            # Get user's 2FA data
            user_2fa_key = f"2fa_user:{user_id}"
            user_2fa_data = await self.redis.hgetall(user_2fa_key)

            if not user_2fa_data or user_2fa_data.get("enabled") != "true":
                logger.warning(f"2FA not enabled for user: {user_id}")
                return False

            secret = user_2fa_data.get("secret")

            # Check if it's a backup code
            if self.is_backup_code(token):
                return await self.verify_backup_code(user_id, token)

            # Verify TOTP token
            return self.verify_token(secret, token)

        except Exception as e:
            logger.error(f"Error verifying 2FA during login: {str(e)}")
            return False

    def generate_backup_codes(self) -> list:
        """Generate backup codes for 2FA recovery."""
        import secrets
        import string

        codes = []
        for _ in range(self.backup_codes_count):
            code = "".join(
                secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8)
            )
            # Format as XXXX-XXXX
            formatted_code = f"{code[:4]}-{code[4:]}"
            codes.append(formatted_code)

        return codes

    def is_backup_code(self, token: str) -> bool:
        """Check if token is in backup code format."""
        return len(token) == 9 and token[4] == "-"

    async def verify_backup_code(self, user_id: str, backup_code: str) -> bool:
        """
        Verify and consume a backup code.

        Args:
            user_id: User ID
            backup_code: Backup code to verify

        Returns:
            True if backup code is valid and unused
        """
        try:
            user_2fa_key = f"2fa_user:{user_id}"
            user_2fa_data = await self.redis.hgetall(user_2fa_key)

            if not user_2fa_data:
                return False

            backup_codes = user_2fa_data.get("backup_codes", "").split(",")

            if backup_code in backup_codes:
                # Remove used backup code
                backup_codes.remove(backup_code)
                await self.redis.hset(
                    user_2fa_key, "backup_codes", ",".join(backup_codes)
                )

                logger.info(f"Backup code used for user: {user_id}")
                return True

            return False

        except Exception as e:
            logger.error(f"Error verifying backup code: {str(e)}")
            return False

    async def get_2fa_status(self, user_id: str) -> Dict[str, Any]:
        """
        Get 2FA status for a user.

        Args:
            user_id: User ID

        Returns:
            Dict containing 2FA status information
        """
        try:
            user_2fa_key = f"2fa_user:{user_id}"
            user_2fa_data = await self.redis.hgetall(user_2fa_key)

            if not user_2fa_data:
                return {"enabled": False, "setup_required": True}

            backup_codes = user_2fa_data.get("backup_codes", "").split(",")
            backup_codes_count = len([code for code in backup_codes if code])

            return {
                "enabled": user_2fa_data.get("enabled") == "true",
                "enabled_at": user_2fa_data.get("enabled_at"),
                "backup_codes_remaining": backup_codes_count,
                "setup_required": False,
            }

        except Exception as e:
            logger.error(f"Error getting 2FA status: {str(e)}")
            return {"enabled": False, "error": str(e)}

    async def start_2fa_setup(self, user_id: str, user_email: str) -> Dict[str, Any]:
        """
        Start 2FA setup process.

        Args:
            user_id: User ID
            user_email: User's email

        Returns:
            Dict containing setup data (secret and QR code)
        """
        try:
            # Generate secret
            secret = self.generate_secret(user_email)

            # Store temporarily (expires in 10 minutes)
            temp_secret_key = f"2fa_temp_secret:{user_id}"
            await self.redis.setex(temp_secret_key, 600, secret)

            # Generate QR code
            qr_code = self.generate_qr_code(user_email, secret)

            return {
                "success": True,
                "secret": secret,
                "qr_code": qr_code,
                "message": "Scan the QR code with your authenticator app",
            }

        except Exception as e:
            logger.error(f"Error starting 2FA setup: {str(e)}")
            return {"success": False, "message": "Failed to start 2FA setup"}
