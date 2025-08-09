"""
Tests for Notification Service Business Logic
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
import asyncio


class TestNotificationService:
    """Test cases for notification service business logic."""

    @pytest.mark.asyncio
    async def test_email_notification_sending(self):
        """Test email notification sending logic."""
        from services.notification_service import NotificationService
        
        # Mock email provider
        with patch("services.notification_service.EmailProvider") as mock_email:
            mock_email.return_value.send_email = AsyncMock(return_value=True)
            
            service = NotificationService()
            result = await service.send_email_notification(
                recipient="test@example.com",
                template="order_confirmation",
                data={"order_id": "123", "customer_name": "John"}
            )
            
            assert result["status"] == "sent"
            mock_email.return_value.send_email.assert_called_once()

    @pytest.mark.asyncio
    async def test_sms_notification_sending(self):
        """Test SMS notification sending logic."""
        from services.notification_service import NotificationService
        
        # Mock SMS provider
        with patch("services.notification_service.SMSProvider") as mock_sms:
            mock_sms.return_value.send_sms = AsyncMock(return_value=True)
            
            service = NotificationService()
            result = await service.send_sms_notification(
                recipient="+1234567890",
                template="order_update",
                data={"order_id": "456", "status": "shipped"}
            )
            
            assert result["status"] == "sent"
            mock_sms.return_value.send_sms.assert_called_once()

    @pytest.mark.asyncio
    async def test_notification_retry_mechanism(self):
        """Test notification retry mechanism on failure."""
        from services.notification_service import NotificationService
        
        with patch("services.notification_service.EmailProvider") as mock_email:
            # First call fails, second succeeds
            mock_email.return_value.send_email = AsyncMock(side_effect=[False, True])
            
            service = NotificationService()
            result = await service.send_notification_with_retry(
                recipient="test@example.com",
                template="test",
                data={},
                max_retries=2
            )
            
            assert result["status"] == "sent"
            assert mock_email.return_value.send_email.call_count == 2

    @pytest.mark.asyncio
    async def test_template_rendering(self):
        """Test notification template rendering."""
        from services.notification_service import NotificationService
        
        service = NotificationService()
        template_content = "Hello {{customer_name}}, your order {{order_id}} is confirmed."
        data = {"customer_name": "John Doe", "order_id": "ORD123"}
        
        rendered = service.render_template(template_content, data)
        
        assert rendered == "Hello John Doe, your order ORD123 is confirmed."

    @pytest.mark.asyncio
    async def test_bulk_notification_processing(self):
        """Test bulk notification processing."""
        from services.notification_service import NotificationService
        
        with patch("services.notification_service.EmailProvider") as mock_email:
            mock_email.return_value.send_email = AsyncMock(return_value=True)
            
            service = NotificationService()
            notifications = [
                {
                    "recipient": "user1@example.com",
                    "template": "promotion",
                    "data": {"discount": "20%"}
                },
                {
                    "recipient": "user2@example.com", 
                    "template": "promotion",
                    "data": {"discount": "15%"}
                }
            ]
            
            results = await service.send_bulk_notifications(notifications)
            
            assert results["sent"] == 2
            assert results["failed"] == 0
            assert mock_email.return_value.send_email.call_count == 2

    @pytest.mark.asyncio
    async def test_notification_status_tracking(self):
        """Test notification status tracking."""
        from services.notification_service import NotificationService
        
        with patch("core.database.get_db") as mock_db:
            mock_session = Mock()
            mock_db.return_value = mock_session
            
            service = NotificationService()
            
            # Test status update
            await service.update_notification_status("notif_123", "delivered")
            
            # Verify database interaction
            mock_session.execute.assert_called()

    def test_notification_validation(self):
        """Test notification data validation."""
        from services.notification_service import NotificationService
        
        service = NotificationService()
        
        # Valid notification
        valid_data = {
            "user_id": "user_123",
            "type": "email",
            "template": "order_confirmation",
            "recipient": "test@example.com",
            "data": {"order_id": "123"}
        }
        
        assert service.validate_notification_data(valid_data) is True
        
        # Invalid notification - missing required fields
        invalid_data = {
            "user_id": "",
            "type": "invalid_type"
        }
        
        assert service.validate_notification_data(invalid_data) is False

    @pytest.mark.asyncio
    async def test_notification_delivery_failure_handling(self):
        """Test handling of notification delivery failures."""
        from services.notification_service import NotificationService
        
        with patch("services.notification_service.EmailProvider") as mock_email:
            mock_email.return_value.send_email = AsyncMock(
                side_effect=Exception("SMTP server unavailable")
            )
            
            service = NotificationService()
            result = await service.send_notification(
                recipient="test@example.com",
                template="test",
                data={}
            )
            
            assert result["status"] == "failed"
            assert "error" in result
