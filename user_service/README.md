# User Service

A microservice for user management in the Food & Fast E-Commerce platform, built with FastAPI and PostgreSQL.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Redis 7+

### Local Development

1. **Setup environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure environment**
   ```bash
   cp config.example.env .env
   # Edit .env with your database and Redis settings
   ```

3. **Start dependencies**
   ```bash
   # Using Docker
   docker run -d --name postgres -e POSTGRES_PASSWORD=password -e POSTGRES_DB=user_db -p 5432:5432 postgres:15
   docker run -d --name redis -p 6379:6379 redis:7-alpine
   ```

4. **Run the service**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8002
   ```

5. **Access endpoints**
   - API: http://localhost:8002
   - Docs: http://localhost:8002/docs
   - Health: http://localhost:8002/health

### Docker Development
```bash
# Using docker-compose
docker-compose up --build

# Or manual Docker
docker build -f Dockerfile.dev -t user-service-dev .
docker run -p 8002:8002 --env-file .env user-service-dev
```

## 🛠 Tech Stack

- **Framework**: FastAPI with async support
- **Database**: PostgreSQL with asyncpg
- **ORM**: SQLAlchemy 2.0
- **Cache**: Redis
- **Auth**: JWT + Google OAuth
- **Validation**: Pydantic
- **Testing**: pytest with async support
- **Code Quality**: Ruff, Black, MyPy

## 📁 Project Structure

```
user_service/
├── app/
│   ├── controllers/          # API routes
│   ├── db/                   # Database setup
│   ├── models/               # SQLAlchemy models
│   ├── schemas/              # Pydantic schemas
│   ├── services/             # Business logic
│   ├── tests/                # Test suite
│   └── utils/                # Utilities
├── k8s/                      # Kubernetes configs
├── monitoring/               # Prometheus/Grafana
├── scripts/                  # Deployment scripts
├── main.py                   # FastAPI app
├── requirements.txt          # Dependencies
├── Dockerfile               # Production build
├── docker-compose.yml       # Local development
└── Makefile                 # Development tasks
```

## 🔌 API Endpoints

### Authentication
- `POST /users/google` - Google OAuth login
- `POST /users/login` - Traditional login
- `POST /users/refresh` - Refresh JWT token

### User Management
- `POST /users/` - Create user
- `GET /users/{user_id}` - Get user by ID
- `PUT /users/{user_id}` - Update user
- `DELETE /users/{user_id}` - Soft delete user
- `GET /users/` - List users (paginated)
- `GET /users/me` - Get current user

### System
- `GET /health` - Health check
- `GET /docs` - API documentation

## ⚙️ Configuration

### Environment Variables
```env
# App Settings
HOST=0.0.0.0
PORT=8002
DEBUG=true

# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/user_db
DATABASE_POOL_SIZE=20

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Google OAuth (optional)
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
```

## 🧪 Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Specific test file
pytest app/tests/test_user_api.py
```

## 🔍 Code Quality

```bash
# Linting and formatting
ruff check .
black --check .
mypy app/

# Auto-fix
ruff check --fix .
black .
```

## 🚀 Deployment

### Production Docker
```bash
docker build -t user-service:latest .
docker run -d --name user-service -p 8002:8002 --env-file .env user-service:latest
```

### Kubernetes
```bash
kubectl apply -f k8s/
```

### Using Makefile
```bash
make build      # Build Docker image
make test       # Run tests
make lint       # Run linting
make deploy     # Deploy to staging
```

## 📊 Monitoring

### Health Check
```bash
curl http://localhost:8002/health
```

### Metrics (Prometheus)
- Request/response metrics
- Database connection status
- Redis connection status

### Logging
- Structured JSON logging
- Configurable log levels
- Request/response logging

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Write comprehensive tests
- Update documentation
- Ensure CI checks pass

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🆘 Support

- Create an issue in the repository
- Check API documentation at `/docs`
- Review test files for usage examples