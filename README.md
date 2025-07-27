# Notification Service

## Overview

The Notification Service is a microservice responsible for handling all types of notifications in the Food & Fast E-Commerce platform. It manages email notifications, SMS messages, push notifications, and in-app notifications with support for multiple channels and templating systems.

## Features

- 📧 **Email Notifications**: Transactional emails with HTML templates
- 📱 **SMS Notifications**: Text message delivery via multiple providers
- 🔔 **Push Notifications**: Mobile and web push notifications
- 💬 **In-App Notifications**: Real-time in-app messaging
- 📋 **Template Management**: Dynamic template system with variables
- 📊 **Notification Analytics**: Delivery tracking and analytics
- 🔄 **Retry Mechanism**: Automatic retry for failed notifications
- 📱 **Multi-Channel Support**: Email, SMS, push, webhook channels

## Tech Stack

- **Framework**: FastAPI
- **Email**: FastAPI-Mail, SMTP
- **SMS**: Twilio, AWS SNS
- **Push Notifications**: Firebase Cloud Messaging
- **Templates**: Jinja2 templating engine
- **Queue**: Redis/RabbitMQ for async processing
- **Validation**: Pydantic
- **Testing**: pytest

## Project Structure

```
notification_service/
├── channels/            # Notification channels
│   ├── email.py        # Email notification channel
│   └── sms.py          # SMS notification channel
├── support/             # Support features
│   └── chat_service.py # Chat support system
├── templates/           # Notification templates
│   ├── email/          # Email templates
│   └── sms/            # SMS templates
├── main.py             # FastAPI application entry point
├── requirements.txt    # Python dependencies
└── Dockerfile         # Docker configuration
```

## API Endpoints

### Notifications
- `POST /notifications/send` - Send notification
- `POST /notifications/bulk-send` - Send bulk notifications
- `GET /notifications/{notification_id}` - Get notification details
- `GET /notifications/user/{user_id}` - Get user notifications
- `PUT /notifications/{notification_id}/status` - Update notification status

### Email Notifications
- `POST /email/send` - Send email notification
- `POST /email/template` - Send templated email
- `GET /email/templates` - List email templates
- `POST /email/templates` - Create email template
- `PUT /email/templates/{template_id}` - Update email template

### SMS Notifications
- `POST /sms/send` - Send SMS notification
- `POST /sms/bulk-send` - Send bulk SMS
- `GET /sms/templates` - List SMS templates
- `POST /sms/templates` - Create SMS template

### Push Notifications
- `POST /push/send` - Send push notification
- `POST /push/topic` - Send topic-based push
- `POST /push/device` - Send device-specific push
- `GET /push/devices/{user_id}` - Get user devices

### Chat Support
- `POST /chat/message` - Send chat message
- `GET /chat/conversations/{user_id}` - Get user conversations
- `POST /chat/conversations` - Create new conversation
- `PUT /chat/conversations/{conversation_id}/status` - Update conversation status

### Analytics
- `GET /analytics/delivery` - Delivery statistics
- `GET /analytics/channels` - Channel usage analytics
- `GET /analytics/templates` - Template performance
- `GET /analytics/errors` - Error tracking

## Environment Variables

Create a `.env` file in the notification_service directory:

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/notification_db

# Application
HOST=0.0.0.0
PORT=8006
DEBUG=true

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_TLS=true
SMTP_SSL=false

# SMS Configuration (Twilio)
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone_number

# SMS Configuration (AWS SNS)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1

# Push Notifications (Firebase)
FIREBASE_CREDENTIALS_PATH=path/to/firebase-credentials.json
FIREBASE_PROJECT_ID=your_firebase_project_id

# Redis
REDIS_URL=redis://localhost:6379

# Notification Configuration
MAX_RETRY_ATTEMPTS=3
RETRY_DELAY_SECONDS=60
NOTIFICATION_TIMEOUT_SECONDS=30
BULK_NOTIFICATION_LIMIT=1000

# Template Configuration
TEMPLATE_CACHE_TTL=3600
DEFAULT_LANGUAGE=en
SUPPORTED_LANGUAGES=en,vi

# Logging
LOG_LEVEL=INFO
```

## Installation & Setup

### Prerequisites
- Python 3.8+
- PostgreSQL
- Redis
- Email service (Gmail, SendGrid, etc.)
- SMS service (Twilio, AWS SNS)
- Push notification service (Firebase)

### Local Development

1. **Clone the repository**
   ```bash
   cd notification_service
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your service credentials
   ```

5. **Run database migrations**
   ```bash
   # Create tables (if using SQLAlchemy create_all)
   python -c "from models import Base; from database import engine; Base.metadata.create_all(engine)"
   ```

6. **Start the service**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8006
   ```

### Docker

1. **Build the image**
   ```bash
   docker build -t notification-service .
   ```

2. **Run the container**
   ```bash
   docker run -p 8006:8006 --env-file .env notification-service
   ```

## Testing

### Run all tests
```bash
pytest
```

### Run with coverage
```bash
pytest --cov=.
```

### Run specific test file
```bash
pytest tests/test_email.py
```

## API Documentation

Once the service is running, you can access:
- **Swagger UI**: http://localhost:8006/docs
- **ReDoc**: http://localhost:8006/redoc
- **Health Check**: http://localhost:8006/health

## Database Schema

### Notifications Table
- `id`: Primary key
- `user_id`: Foreign key to users
- `type`: Notification type (email, sms, push, in_app)
- `channel`: Notification channel
- `template_id`: Template identifier
- `subject`: Notification subject
- `content`: Notification content
- `status`: Delivery status (pending, sent, delivered, failed)
- `sent_at`: Sent timestamp
- `delivered_at`: Delivered timestamp
- `created_at`: Creation timestamp

### Templates Table
- `id`: Primary key
- `name`: Template name
- `type`: Template type (email, sms, push)
- `subject`: Template subject
- `content`: Template content
- `variables`: Template variables (JSON)
- `language`: Template language
- `is_active`: Template status
- `created_at`: Creation timestamp

### Notification Logs Table
- `id`: Primary key
- `notification_id`: Foreign key to notifications
- `attempt`: Attempt number
- `status`: Attempt status
- `error_message`: Error details
- `provider_response`: Provider response
- `created_at`: Attempt timestamp

## Notification Channels

### Email Channel
- **Providers**: Gmail, SendGrid, AWS SES, SMTP
- **Features**: HTML templates, attachments, bulk sending
- **Templates**: Order confirmation, password reset, welcome email
- **Tracking**: Open tracking, click tracking

### SMS Channel
- **Providers**: Twilio, AWS SNS, Vonage
- **Features**: Text messages, bulk SMS, delivery reports
- **Templates**: Order updates, delivery notifications
- **Limitations**: Character limits, delivery time

### Push Notifications
- **Providers**: Firebase Cloud Messaging, Apple Push Notifications
- **Features**: Mobile and web push, topic-based messaging
- **Templates**: Promotional messages, order updates
- **Targeting**: Device-specific, user-specific, topic-based

### In-App Notifications
- **Features**: Real-time messaging, persistent notifications
- **Templates**: System announcements, user alerts
- **Delivery**: WebSocket, Server-Sent Events

## Template System

### Template Variables
- `{{user.name}}`: User's name
- `{{order.id}}`: Order ID
- `{{order.total}}`: Order total
- `{{product.name}}`: Product name
- `{{delivery_date}}`: Delivery date

### Template Types
- **Order Confirmation**: Order details and tracking
- **Password Reset**: Reset link and instructions
- **Welcome Email**: User onboarding
- **Delivery Update**: Shipping status
- **Promotional**: Marketing campaigns

### Multi-language Support
- Template localization
- Language detection
- Fallback templates
- RTL language support

## Notification Types

### Transactional Notifications
- **Order Confirmation**: Order placed successfully
- **Payment Confirmation**: Payment received
- **Shipping Update**: Order shipped/delivered
- **Account Verification**: Email verification
- **Password Reset**: Password reset link

### Marketing Notifications
- **Welcome Series**: New user onboarding
- **Promotional Offers**: Discounts and deals
- **Abandoned Cart**: Cart recovery
- **Product Recommendations**: Personalized suggestions
- **Newsletter**: Regular updates

### System Notifications
- **Maintenance Alerts**: System maintenance
- **Security Alerts**: Account security
- **Policy Updates**: Terms and conditions
- **Feature Announcements**: New features

## Delivery Tracking

### Status Tracking
- **Pending**: Notification queued
- **Sending**: In transit to provider
- **Sent**: Delivered to provider
- **Delivered**: Successfully delivered
- **Failed**: Delivery failed
- **Bounced**: Email bounced

### Analytics
- **Delivery Rate**: Success/failure ratio
- **Open Rate**: Email open tracking
- **Click Rate**: Link click tracking
- **Response Time**: Delivery time metrics
- **Channel Performance**: Channel comparison

## Error Handling

### Common Errors
- **Invalid Email**: Malformed email address
- **SMS Limit**: Rate limiting for SMS
- **Template Error**: Missing template variables
- **Provider Error**: Service provider issues
- **Network Error**: Connection problems

### Retry Mechanism
- **Exponential Backoff**: Increasing delay between retries
- **Max Retries**: Configurable retry limit
- **Error Classification**: Different retry strategies
- **Dead Letter Queue**: Failed notification storage

## Performance Features

- **Async Processing**: Background notification processing
- **Bulk Sending**: Efficient bulk notification delivery
- **Caching**: Template and configuration caching
- **Rate Limiting**: Provider rate limit management
- **Connection Pooling**: Database and provider connections

## Security Features

- **Template Sanitization**: XSS prevention
- **Rate Limiting**: Abuse prevention
- **Authentication**: API key validation
- **Encryption**: Sensitive data encryption
- **Audit Logging**: Notification audit trail

## Monitoring & Logging

- **Health Checks**: `/health` endpoint for service monitoring
- **Delivery Tracking**: Comprehensive delivery status tracking
- **Error Logging**: Detailed error logging for debugging
- **Performance Metrics**: Notification processing time
- **Business Metrics**: Delivery rates and engagement

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is part of the Food & Fast E-Commerce platform. 