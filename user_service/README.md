# User Service - Food & Fast E-Commerce Platform

A robust microservice for managing user accounts in the Food & Fast E-Commerce platform, built with FastAPI and PostgreSQL.

## 🚀 Features

- **User Management**: Complete CRUD operations for user accounts
- **Authentication**: JWT-based authentication with Google OAuth integration
- **Security**: Password hashing, input validation, and security best practices
- **Caching**: Redis-based caching for improved performance
- **Async Operations**: Full async/await support with PostgreSQL
- **API Documentation**: Auto-generated Swagger/OpenAPI documentation
- **Testing**: Comprehensive test suite with pytest
- **Docker Support**: Production and development Docker configurations
- **CI/CD**: Automated testing, linting, and deployment pipeline

## 🛠 Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) - Modern, fast web framework
- **Database**: [PostgreSQL](https://www.postgresql.org/) with [asyncpg](https://github.com/MagicStack/asyncpg)
- **ORM**: [SQLAlchemy](https://www.sqlalchemy.org/) 2.0 with async support
- **Cache**: [Redis](https://redis.io/) for session and data caching
- **Authentication**: [JWT](https://jwt.io/) + [Google OAuth](https://developers.google.com/identity/protocols/oauth2)
- **Validation**: [Pydantic](https://pydantic-docs.helpmanual.io/) for data validation
- **Testing**: [pytest](https://pytest.org/) with async support
- **Code Quality**: [Ruff](https://github.com/astral-sh/ruff), [Black](https://black.readthedocs.io/), [MyPy](https://mypy.readthedocs.io/)

## 📁 Project Structure

```
user_service/
├── app/
│   ├── config.py              # Application configuration
│   ├── controllers/           # API route handlers
│   │   └── user_router.py     # User endpoints
│   ├── db/                    # Database configuration
│   │   ├── base.py           # Base database setup
│   │   └── database.py       # Database connection
│   ├── dependencies.py        # FastAPI dependencies
│   ├── models/               # SQLAlchemy models
│   │   └── user.py           # User model
│   ├── schemas/              # Pydantic schemas
│   │   └── user.py           # Request/Response schemas
│   ├── services/             # Business logic
│   │   └── user_service.py   # User service layer
│   ├── tests/                # Test files
│   │   ├── conftest.py       # Test configuration
│   │   ├── test_user_api.py  # API tests
│   │   └── test_user_service.py # Service tests
│   └── utils/                # Utility functions
│       ├── jwt_helper.py     # JWT utilities
│       └── redis_client.py   # Redis client
├── .github/
│   └── workflows/
│       └── ci-user-service.yml # CI/CD pipeline
├── main.py                   # FastAPI application entry point
├── requirements.txt          # Python dependencies
├── Dockerfile               # Production Docker configuration
├── Dockerfile.dev          # Development Docker configuration
├── .dockerignore           # Docker ignore file
└── README.md               # This file
```

## 🔌 API Endpoints

### Authentication
- `POST /users/google` - Google OAuth login/registration
- `POST /users/login` - Traditional login
- `POST /users/refresh` - Refresh JWT token

### User Management
- `POST /users/` - Create new user
- `GET /users/{user_id}` - Get user by ID
- `PUT /users/{user_id}` - Update user profile
- `DELETE /users/{user_id}` - Soft delete user
- `GET /users/` - List users with pagination
- `GET /users/me` - Get current user profile

### Health & Monitoring
- `GET /health` - Health check endpoint
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation (ReDoc)

## ⚙️ Environment Variables

Create a `.env` file in the project root:

```env
# Application Settings
HOST=0.0.0.0
PORT=8002
DEBUG=true
ENVIRONMENT=development

# Database Configuration
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/user_db
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
REDIS_POOL_SIZE=10

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Google OAuth (Optional)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8002/users/google/callback

# Security
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (optional)

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
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

5. **Start PostgreSQL and Redis**
   ```bash
   # Using Docker
   docker run -d --name postgres -e POSTGRES_PASSWORD=password -e POSTGRES_DB=user_db -p 5432:5432 postgres:15
   docker run -d --name redis -p 6379:6379 redis:7-alpine
   
   # Or use your local installations
   ```

6. **Run the application**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8002
   ```

7. **Access the API**
   - API: http://localhost:8002
   - Documentation: http://localhost:8002/docs
   - Health Check: http://localhost:8002/health

### Docker Development

```bash
# Build development image
docker build -f Dockerfile.dev -t user-service-dev .

# Run with environment file
docker run -p 8002:8002 --env-file .env user-service-dev

# Or use docker-compose (if available)
docker-compose up --build
```

### Production Deployment

```bash
# Build production image
docker build -t user-service:latest .

# Run production container
docker run -d \
  --name user-service \
  -p 8002:8002 \
  --env-file .env \
  user-service:latest
```

## 🧪 Testing

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest app/tests/test_user_api.py

# Run with verbose output
pytest -v

# Run tests in parallel
pytest -n auto
```

### Test Coverage

```bash
# Generate coverage report
pytest --cov=app --cov-report=html --cov-report=term-missing

# View coverage report
open htmlcov/index.html  # On macOS
# or
start htmlcov/index.html  # On Windows
```

## 🔍 Code Quality

### Linting and Formatting

```bash
# Run all quality checks
ruff check .
black --check .
mypy app/

# Auto-fix issues
ruff check --fix .
black .
```

### Security Checks

```bash
# Run security linter
bandit -r app/

# Check for vulnerable dependencies
safety check
```

## 🚀 CI/CD Pipeline

The project includes a comprehensive GitHub Actions CI/CD pipeline that:

### Automated Checks
- **Linting**: Ruff, Black, Flake8
- **Type Checking**: MyPy
- **Security**: Bandit, Safety
- **Testing**: Pytest with coverage
- **Docker Build**: Multi-platform builds

### Deployment Stages
- **Staging**: Automatic deployment on `develop` branch
- **Production**: Manual deployment on `main` branch

### Pipeline Features
- Caching for faster builds
- Parallel job execution
- Multi-platform Docker images
- Code coverage reporting
- Security vulnerability scanning

## 📊 Monitoring & Health Checks

### Health Endpoint
```bash
curl http://localhost:8002/health
```

Response:
```json
{
  "status": "healthy",
  "service": "user_service",
  "timestamp": "2024-01-01T00:00:00Z",
  "version": "1.0.0"
}
```

### Metrics (Future Enhancement)
- Request/response metrics
- Database connection pool status
- Redis connection status
- Custom business metrics

## 🔧 Configuration

### Database Configuration
The service supports both development and production database configurations:

```python
# Development
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/user_db

# Production with connection pooling
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/user_db?pool_size=20&max_overflow=30
```

### Redis Configuration
```python
# Basic Redis
REDIS_URL=redis://localhost:6379/0

# Redis with authentication
REDIS_URL=redis://:password@localhost:6379/0

# Redis Cluster
REDIS_URL=redis://host1:6379,host2:6379,host3:6379/0
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Write comprehensive tests
- Update documentation
- Ensure all CI checks pass

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the test files for usage examples

## 🔄 Changelog

### v1.0.0 (2024-01-01)
- Initial release
- User CRUD operations
- JWT authentication
- Google OAuth integration
- Redis caching
- Comprehensive test suite
- Docker support
- CI/CD pipeline