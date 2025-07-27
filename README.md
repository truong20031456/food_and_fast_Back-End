# Auth Service

## Overview

The Auth Service is a microservice responsible for handling user authentication, authorization, and user management in the Food & Fast E-Commerce platform. It provides secure JWT-based authentication, user registration, password management, and profile management capabilities.

## Features

- 🔐 **JWT Authentication**: Secure token-based authentication
- 👤 **User Management**: User registration, profile management, and account operations
- 🔒 **Password Security**: Secure password hashing with bcrypt
- 📧 **Email Verification**: Email-based account verification
- 🔄 **Token Management**: JWT token refresh and validation
- 🛡️ **Security**: Rate limiting, CORS, and security headers
- 📊 **Audit Logging**: Comprehensive audit trail for security events
- 🗄️ **Caching**: Redis-based caching for improved performance

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL (async)
- **Cache**: Redis
- **Authentication**: JWT with python-jose
- **Password Hashing**: bcrypt
- **Email**: FastAPI-Mail
- **Validation**: Pydantic
- **Testing**: pytest

## Project Structure

```
auth_service/
├── controllers/          # API route handlers
│   ├── auth_controller.py
│   └── __init__.py
├── core/                # Core configuration and database
│   ├── config.py        # Application settings
│   ├── database.py      # Database connection
│   └── dependencies.py  # FastAPI dependencies
├── models/              # SQLAlchemy models
│   ├── base.py
│   └── user.py
├── schemas/             # Pydantic schemas
│   ├── auth.py
│   ├── user.py
│   ├── token.py
│   └── common.py
├── services/            # Business logic
│   ├── auth_service.py
│   ├── user_service.py
│   ├── token_service.py
│   ├── cache_service.py
│   └── audit_service.py
├── utils/               # Utility functions
│   ├── security.py
│   └── logger.py
├── tests/               # Test files
├── migrations/          # Database migrations
├── main.py             # FastAPI application entry point
├── requirements.txt    # Python dependencies
└── Dockerfile         # Docker configuration
```

## API Endpoints

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout
- `POST /auth/refresh` - Refresh JWT token

### User Management
- `GET /users/me` - Get current user profile
- `PUT /users/me` - Update user profile
- `DELETE /users/me` - Delete user account
- `GET /users/{user_id}` - Get user by ID (admin)

### Password Management
- `POST /passwords/forgot` - Request password reset
- `POST /passwords/reset` - Reset password
- `PUT /passwords/change` - Change password

### Token Management
- `POST /tokens/validate` - Validate JWT token
- `POST /tokens/revoke` - Revoke JWT token

### Profile Management
- `GET /profile` - Get user profile
- `PUT /profile` - Update user profile
- `POST /profile/avatar` - Upload profile avatar

## Environment Variables

Create a `.env` file in the auth_service directory:

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/auth_db
SYNC_DATABASE_URL=postgresql://user:password@localhost:5432/auth_db

# Redis
REDIS_URL=redis://localhost:6379

# JWT
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Security
SECRET_KEY=your-secret-key
BCRYPT_ROUNDS=12

# CORS
CORS_ORIGINS=["http://localhost:3000", "https://yourdomain.com"]

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60

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

5. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

6. **Start the service**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8001
   ```

### Docker

1. **Build the image**
   ```bash
   docker build -t auth-service .
   ```

2. **Run the container**
   ```bash
   docker run -p 8001:8001 --env-file .env auth-service
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
pytest tests/test_auth.py
```

## API Documentation

Once the service is running, you can access:
- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc
- **Health Check**: http://localhost:8001/health

## Security Features

- **Password Hashing**: Uses bcrypt with configurable rounds
- **JWT Tokens**: Secure token-based authentication
- **Rate Limiting**: Prevents brute force attacks
- **CORS**: Configurable cross-origin resource sharing
- **Input Validation**: Pydantic-based request validation
- **Audit Logging**: Comprehensive security event logging

## Monitoring & Logging

- **Health Checks**: `/health` endpoint for service monitoring
- **Structured Logging**: Uses structlog for consistent log format
- **Audit Trail**: All security events are logged
- **Metrics**: Prometheus metrics for monitoring

## Database Schema

### Users Table
- `id`: Primary key
- `email`: Unique email address
- `username`: Unique username
- `hashed_password`: Bcrypt hashed password
- `is_active`: Account status
- `is_verified`: Email verification status
- `created_at`: Account creation timestamp
- `updated_at`: Last update timestamp

### Tokens Table
- `id`: Primary key
- `user_id`: Foreign key to users
- `token_hash`: Hashed JWT token
- `token_type`: Token type (access/refresh)
- `expires_at`: Token expiration
- `is_revoked`: Token revocation status

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is part of the Food & Fast E-Commerce platform. 