# User Service

## Overview

The User Service is a microservice responsible for managing user profiles, preferences, addresses, and user-related data in the Food & Fast E-Commerce platform. It provides comprehensive user management capabilities including profile management, address book, preferences, and user data analytics.

## Features

- 👤 **User Profile Management**: Complete user profile CRUD operations
- 📍 **Address Management**: Multiple address support with validation
- ⚙️ **User Preferences**: Customizable user preferences and settings
- 📊 **User Analytics**: User behavior and engagement tracking
- 🔐 **Profile Security**: Secure profile data handling
- 📱 **Multi-Platform Support**: Web and mobile user management
- 🔄 **Data Synchronization**: Real-time profile updates
- 📋 **User Segmentation**: User categorization and targeting

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL (async)
- **Cache**: Redis
- **Authentication**: JWT integration
- **Validation**: Pydantic
- **Testing**: pytest
- **Documentation**: Auto-generated OpenAPI/Swagger

## Project Structure

```
user_service/
├── app/
│   ├── config.py        # Application configuration
│   ├── controllers/     # API route handlers
│   │   └── user_router.py
│   ├── db/             # Database configuration
│   │   ├── base.py
│   │   └── database.py
│   ├── dependencies.py  # FastAPI dependencies
│   ├── middleware/      # Custom middleware
│   ├── models/          # SQLAlchemy models
│   │   └── user.py
│   ├── schemas/         # Pydantic schemas
│   │   └── user.py
│   ├── services/        # Business logic
│   │   └── user_service.py
│   ├── tests/           # Test files
│   │   ├── conftest.py
│   │   ├── test_user_api.py
│   │   └── test_user_service.py
│   └── utils/           # Utility functions
│       ├── jwt_helper.py
│       └── redis_client.py
├── main.py             # FastAPI application entry point
├── requirements.txt    # Python dependencies
└── Dockerfile         # Docker configuration
```

## API Endpoints

### User Profiles
- `GET /users/profile` - Get current user profile
- `PUT /users/profile` - Update user profile
- `DELETE /users/profile` - Delete user account
- `GET /users/{user_id}` - Get user by ID (admin)
- `PUT /users/{user_id}` - Update user by ID (admin)
- `DELETE /users/{user_id}` - Delete user by ID (admin)

### User Addresses
- `GET /users/addresses` - Get user addresses
- `POST /users/addresses` - Add new address
- `GET /users/addresses/{address_id}` - Get address details
- `PUT /users/addresses/{address_id}` - Update address
- `DELETE /users/addresses/{address_id}` - Delete address
- `PUT /users/addresses/{address_id}/default` - Set default address

### User Preferences
- `GET /users/preferences` - Get user preferences
- `PUT /users/preferences` - Update user preferences
- `POST /users/preferences/reset` - Reset preferences to default
- `GET /users/preferences/notifications` - Get notification preferences
- `PUT /users/preferences/notifications` - Update notification preferences

### User Analytics
- `GET /users/analytics/activity` - Get user activity analytics
- `GET /users/analytics/preferences` - Get preference analytics
- `GET /users/analytics/engagement` - Get engagement metrics
- `GET /users/analytics/segments` - Get user segmentation data

### User Management (Admin)
- `GET /users` - List all users with pagination
- `POST /users/bulk-update` - Bulk update users
- `GET /users/search` - Search users
- `POST /users/export` - Export user data
- `GET /users/statistics` - User statistics

## Environment Variables

Create a `.env` file in the user_service directory:

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/user_db

# Application
HOST=0.0.0.0
PORT=8005
DEBUG=true

# Redis
REDIS_URL=redis://localhost:6379

# JWT Configuration
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Service URLs
AUTH_SERVICE_URL=http://localhost:8001
NOTIFICATION_SERVICE_URL=http://localhost:8006

# User Configuration
MAX_ADDRESSES_PER_USER=10
PROFILE_IMAGE_MAX_SIZE=5242880  # 5MB
ALLOWED_IMAGE_TYPES=jpg,jpeg,png,webp

# Pagination
DEFAULT_PAGE_SIZE=20
MAX_PAGE_SIZE=100

# Cache Configuration
CACHE_TTL=3600
USER_CACHE_PREFIX=user_profile

# Logging
LOG_LEVEL=INFO
```

## Installation & Setup

### Prerequisites
- Python 3.8+
- PostgreSQL
- Redis

### Local Development

1. **Clone the repository**
   ```bash
   cd user_service
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
   # Edit .env with your configuration
   ```

5. **Run database migrations**
   ```bash
   # Create tables (if using SQLAlchemy create_all)
   python -c "from app.db.base import Base; from app.db.database import engine; Base.metadata.create_all(engine)"
   ```

6. **Start the service**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8005
   ```

### Docker

1. **Build the image**
   ```bash
   docker build -t user-service .
   ```

2. **Run the container**
   ```bash
   docker run -p 8005:8005 --env-file .env user-service
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
pytest app/tests/test_user_api.py
```

### Run service tests
```bash
pytest app/tests/test_user_service.py
```

## API Documentation

Once the service is running, you can access:
- **Swagger UI**: http://localhost:8005/docs
- **ReDoc**: http://localhost:8005/redoc
- **Health Check**: http://localhost:8005/health

## Database Schema

### Users Table
- `id`: Primary key
- `email`: User email address
- `username`: Username
- `first_name`: First name
- `last_name`: Last name
- `phone`: Phone number
- `date_of_birth`: Date of birth
- `gender`: Gender (male, female, other)
- `profile_image`: Profile image URL
- `is_active`: Account status
- `created_at`: Account creation timestamp
- `updated_at`: Last update timestamp

### User Addresses Table
- `id`: Primary key
- `user_id`: Foreign key to users
- `address_type`: Address type (home, work, other)
- `is_default`: Default address flag
- `street_address`: Street address
- `city`: City
- `state`: State/province
- `postal_code`: Postal code
- `country`: Country
- `latitude`: GPS latitude
- `longitude`: GPS longitude
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### User Preferences Table
- `id`: Primary key
- `user_id`: Foreign key to users
- `preference_key`: Preference key
- `preference_value`: Preference value (JSON)
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### User Activity Table
- `id`: Primary key
- `user_id`: Foreign key to users
- `activity_type`: Activity type
- `activity_data`: Activity data (JSON)
- `ip_address`: User IP address
- `user_agent`: User agent string
- `created_at`: Activity timestamp

## User Profile Features

### Profile Management
- **Basic Information**: Name, email, phone, date of birth
- **Profile Images**: Avatar upload and management
- **Account Settings**: Password, email preferences
- **Privacy Settings**: Data sharing preferences

### Address Management
- **Multiple Addresses**: Support for multiple addresses
- **Address Types**: Home, work, delivery addresses
- **Address Validation**: Geographic validation
- **Default Address**: Primary address designation
- **GPS Coordinates**: Location-based services

### User Preferences
- **Language Preferences**: Interface language
- **Currency Preferences**: Display currency
- **Notification Settings**: Email, SMS, push preferences
- **Privacy Settings**: Data sharing and visibility
- **Theme Preferences**: UI theme and appearance

## User Analytics

### Activity Tracking
- **Login Activity**: Login history and patterns
- **Profile Updates**: Profile modification tracking
- **Address Changes**: Address update history
- **Preference Changes**: Preference modification tracking

### Engagement Metrics
- **Profile Completeness**: Profile completion percentage
- **Update Frequency**: Profile update frequency
- **Address Usage**: Address usage patterns
- **Preference Adoption**: Preference setting patterns

### User Segmentation
- **Demographic Segmentation**: Age, gender, location
- **Behavioral Segmentation**: Activity patterns
- **Preference Segmentation**: Preference-based groups
- **Engagement Segmentation**: Engagement level groups

## Integration Points

### Auth Service
- User authentication and authorization
- JWT token validation
- User session management

### Notification Service
- Profile update notifications
- Address change alerts
- Preference update confirmations

### Analytics Service
- User behavior data
- Profile analytics
- Engagement metrics

## Security Features

- **Data Encryption**: Sensitive data encryption
- **Input Validation**: Comprehensive input validation
- **Access Control**: Role-based access control
- **Audit Logging**: User activity audit trail
- **Data Sanitization**: SQL injection prevention

## Performance Features

- **Caching**: Redis-based user profile caching
- **Pagination**: Efficient data pagination
- **Indexing**: Database indexes for fast queries
- **Connection Pooling**: Database connection optimization
- **Async Processing**: Background task processing

## Monitoring & Logging

- **Health Checks**: `/health` endpoint for service monitoring
- **User Activity Tracking**: Comprehensive activity logging
- **Error Logging**: Detailed error logging for debugging
- **Performance Metrics**: Query performance monitoring
- **Business Metrics**: User engagement tracking

## Data Export

### Export Formats
- **CSV**: Comma-separated values
- **JSON**: JavaScript Object Notation
- **Excel**: Microsoft Excel format

### Export Features
- **Filtered Exports**: Data filtering and selection
- **Bulk Export**: Large dataset export
- **Scheduled Exports**: Automated data export
- **Privacy Compliance**: GDPR-compliant exports

## Error Handling

### Common Errors
- **Invalid Data**: Data validation errors
- **User Not Found**: User doesn't exist
- **Permission Denied**: Insufficient permissions
- **Duplicate Data**: Duplicate email/username
- **Validation Errors**: Address validation failures

### Error Recovery
- **Graceful Degradation**: Service continues with partial data
- **User-friendly Messages**: Clear error messages
- **Retry Mechanisms**: Automatic retry for transient errors
- **Fallback Values**: Default values for missing data

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is part of the Food & Fast E-Commerce platform. 