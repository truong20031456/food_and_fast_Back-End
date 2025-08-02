# Auth Service

## Overview

The Auth Service is a microservice responsible for handling user authentication, authorization, and user management in the Food & Fast E-Commerce platform. Built with FastAPI, it provides secure JWT-based authentication, Google OAuth integration, user registration, and comprehensive security features.

## Features

- 🔐 **JWT Authentication**: Secure token-based authentication with access/refresh tokens
- 🌐 **Google OAuth 2.0**: Complete Google OAuth integration with callback handling
- 👤 **User Management**: Registration, profile management, and account operations
- 🔒 **Password Security**: bcrypt hashing with configurable rounds
- 🛡️ **Account Protection**: Login attempt tracking and account lockout (5 attempts, 15-minute lockout)
- 📊 **Audit Logging**: Comprehensive audit trail for all security events
- 🗄️ **Redis Caching**: Rate limiting and session management
- 🔄 **Token Management**: Refresh token rotation and validation
- 📱 **User Profiles**: Complete profile management with preferences

## Tech Stack

- **Framework**: FastAPI with async/await
- **Database**: PostgreSQL (async with asyncpg)
- **Cache**: Redis with aioredis
- **Authentication**: JWT with PyJWT + Google OAuth 2.0
- **Password Hashing**: bcrypt via passlib
- **ORM**: SQLAlchemy with async support
- **Validation**: Pydantic v2
- **Testing**: pytest with asyncio support
- **HTTP Client**: httpx for OAuth requests

## Project Structure

```
auth_service/
├── controllers/              # API route handlers
│   ├── __init__.py          # Router exports
│   └── auth_controller.py   # Auth endpoints (register, login, logout, /me, Google OAuth)
├── core/                    # Core configuration and dependencies
│   └── dependencies.py     # FastAPI dependency injection
├── models/                  # SQLAlchemy models
│   ├── base.py             # Base model with common fields
│   └── user.py             # User model with OAuth fields
├── schemas/                 # Pydantic schemas
│   ├── auth.py             # Auth request/response schemas
│   ├── user.py             # User schemas
│   ├── token.py            # Token schemas
│   └── common.py           # Common response schemas
├── services/                # Business logic layer
│   ├── auth_service.py     # Core authentication logic
│   ├── user_service.py     # User management operations
│   ├── token_service.py    # JWT token operations
│   ├── cache_service.py    # Redis caching operations
│   ├── audit_service.py    # Security audit logging
│   └── google_oauth_service.py # Google OAuth integration
├── utils/                   # Utility functions
│   ├── security.py         # JWT creation and validation
│   ├── logger.py           # Structured logging setup
│   └── jwt_utils.py        # JWT helper functions
├── tests/                   # Test files
│   ├── conftest.py         # Test configuration
│   ├── test_auth.py        # Authentication tests
│   └── test_google_oauth.py # Google OAuth tests
├── migrations/              # Database migrations
│   └── versions/           # Migration files
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── pytest.ini             # Test configuration
├── Dockerfile              # Production Docker image
├── Dockerfile.dev          # Development Docker image
└── GOOGLE_OAUTH_SETUP.md   # Google OAuth setup guide
```

## API Endpoints

### Authentication
- `POST /auth/register` - User registration with email/password
- `POST /auth/login` - User login with credentials
- `POST /auth/logout` - User logout and token invalidation
- `GET /auth/me` - Get current authenticated user profile

### Google OAuth 2.0
- `GET /auth/google/auth-url` - Get Google OAuth authorization URL
- `POST /auth/google` - Authenticate with Google ID/access token
- `POST /auth/google/callback` - Handle Google OAuth callback

## Environment Variables

Create a `.env` file in the auth_service directory:

```env
# Database Configuration
DATABASE_URL=postgresql+asyncpg://truong:truong123@localhost:5432/auth_service_db
DATABASE_ECHO=false

# Security
SECRET_KEY=D_Rzt0rRhDYXUz2k-7jsAcFcPQINXxR0Q0_hLj7iN_4
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Google OAuth Configuration
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:3000/auth/google/callback

# CORS Configuration
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:8080"]

# Logging
LOG_LEVEL=INFO

# Auth Service Specific
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION_MINUTES=15

# Email Configuration (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

## Installation & Setup

### Prerequisites
- Python 3.11+
- PostgreSQL 12+
- Redis 6+

### Local Development

1. **Clone and navigate to auth service**
   ```bash
   cd auth_service
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

5. **Set up Google OAuth** (optional)
   - Follow instructions in `GOOGLE_OAUTH_SETUP.md`
   - Add your Google OAuth credentials to `.env`

6. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

7. **Start the service**
   ```bash
   python main.py
   # or
   uvicorn main:app --reload --host 0.0.0.0 --port 8001
   ```

### Docker Development

1. **Build and run with Docker**
   ```bash
   docker build -f Dockerfile.dev -t auth-service-dev .
   docker run -p 8001:8001 --env-file .env auth-service-dev
   ```

## Testing

### Run all tests
```bash
pytest
```

### Run with coverage
```bash
pytest --cov=auth_service --cov-report=html
```

### Run specific test files
```bash
pytest tests/test_auth.py
pytest tests/test_google_oauth.py
```

### Test Google OAuth
```bash
pytest tests/test_google_oauth.py -v
```

## API Documentation

Once the service is running, access:
- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc
- **Health Check**: http://localhost:8001/health

## Security Features

- **Password Security**: bcrypt hashing with salt rounds
- **JWT Tokens**: HS256 signed tokens with configurable expiration
- **Refresh Tokens**: Secure token rotation with database storage
- **Account Lockout**: 5 failed attempts trigger 15-minute lockout
- **Rate Limiting**: Redis-based rate limiting and caching
- **Audit Logging**: All authentication events logged with IP tracking
- **Google OAuth**: Full OAuth 2.0 flow with token verification
- **Input Validation**: Pydantic schema validation for all requests
- **CORS Protection**: Configurable origins and headers

## Database Schema

### Users Table
- `id`: Primary key (auto-increment)
- `user_uuid`: Unique UUID for external references
- `username`: Optional unique username
- `email`: Required unique email address
- `password_hash`: bcrypt hashed password
- `first_name`, `last_name`: User profile information
- `phone_number`: Optional phone number
- `avatar_url`: Profile picture URL
- `bio`: User biography
- `preferences`: JSON field for user preferences
- `google_id`: Google OAuth user ID
- `google_picture`: Google profile picture URL
- `status`: User status (active, inactive, suspended, pending_verification)
- `is_email_verified`: Email verification status
- `is_phone_verified`: Phone verification status
- `last_login_at`: Last successful login timestamp
- `failed_login_attempts`: Failed login counter
- `locked_until`: Account lockout expiration
- `created_at`, `updated_at`: Timestamp fields

### Refresh Tokens Table
- `id`: Primary key
- `user_id`: Foreign key to users table
- `token_hash`: Hashed refresh token
- `expires_at`: Token expiration timestamp
- `is_revoked`: Token revocation status
- `created_at`: Token creation timestamp

### Audit Logs Table
- `id`: Primary key
- `user_id`: Foreign key to users table (nullable)
- `action`: Action performed (LOGIN_SUCCESS, REGISTRATION_FAILED, etc.)
- `ip_address`: Client IP address
- `details`: JSON field for additional event details
- `created_at`: Event timestamp

## Google OAuth Setup

1. **Create Google OAuth Application**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing
   - Enable Google+ API
   - Create OAuth 2.0 credentials

2. **Configure OAuth Settings**
   - Add authorized redirect URIs
   - Set up consent screen
   - Add test users if needed

3. **Update Environment Variables**
   ```env
   GOOGLE_CLIENT_ID=your-client-id
   GOOGLE_CLIENT_SECRET=your-client-secret
   GOOGLE_REDIRECT_URI=http://localhost:3000/auth/google/callback
   ```

See `GOOGLE_OAUTH_SETUP.md` for detailed instructions.

## Monitoring & Logging

- **Health Checks**: `/health` endpoint for service status
- **Structured Logging**: JSON-formatted logs with correlation IDs
- **Audit Trail**: Complete security event logging
- **Error Tracking**: Comprehensive error logging with stack traces
- **Performance Monitoring**: Request timing and database query logging

## Error Handling

The service implements comprehensive error handling:
- **Validation Errors**: 422 with detailed field validation messages
- **Authentication Errors**: 401 for invalid credentials
- **Authorization Errors**: 403 for insufficient permissions
- **Rate Limiting**: 429 for too many requests
- **Server Errors**: 500 with error tracking and logging

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Make your changes with proper tests
4. Run the test suite: `pytest`
5. Run linting: `ruff check .`
6. Submit a pull request

## License

This project is part of the Food & Fast E-Commerce platform.