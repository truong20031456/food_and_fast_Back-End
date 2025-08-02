.PHONY: help install test lint format clean docker-build docker-run docker-stop docker-logs setup-db migrate

# Default target
help:
	@echo "Available commands:"
	@echo "  install      - Install Python dependencies"
	@echo "  test         - Run tests with coverage"
	@echo "  lint         - Run linting and code quality checks"
	@echo "  format       - Format code with Black and Ruff"
	@echo "  clean        - Clean up cache and temporary files"
	@echo "  docker-build - Build Docker images"
	@echo "  docker-run   - Run services with Docker Compose"
	@echo "  docker-stop  - Stop Docker services"
	@echo "  docker-logs  - Show Docker logs"
	@echo "  setup-db     - Set up database and run migrations"
	@echo "  migrate      - Run database migrations"

# Python environment
install:
	pip install -r requirements.txt

# Testing
test:
	pytest -v --cov=app --cov-report=html --cov-report=term-missing

test-watch:
	pytest -v --cov=app --cov-report=html --cov-report=term-missing -f

# Code quality
lint:
	ruff check .
	black --check .
	mypy app/
	bandit -r app/
	safety check

format:
	ruff check --fix .
	black .
	ruff format .

# Cleanup
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf coverage.xml

# Docker commands
docker-build:
	docker-compose build

docker-run:
	docker-compose up -d

docker-run-dev:
	docker-compose up -d user_service_dev postgres redis

docker-run-prod:
	docker-compose --profile production up -d

docker-stop:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-logs-service:
	docker-compose logs -f user_service_dev

# Database
setup-db:
	docker-compose up -d postgres redis
	sleep 10
	# Add migration commands here when available

migrate:
	# Add migration commands here when available
	echo "Migrations not yet implemented"

# Development tools
dev-tools:
	docker-compose --profile dev-tools up -d pgadmin redis-commander

# Production deployment
deploy-staging:
	echo "Deploying to staging environment..."
	# Add staging deployment commands

deploy-production:
	echo "Deploying to production environment..."
	# Add production deployment commands

# Health checks
health-check:
	curl -f http://localhost:8002/health || echo "Service not running"

# Security
security-scan:
	bandit -r app/ -f json -o bandit-report.json
	safety check --json --output safety-report.json

# Documentation
docs:
	uvicorn main:app --reload --host 0.0.0.0 --port 8002 &
	sleep 5
	echo "API Documentation available at:"
	echo "  - Swagger UI: http://localhost:8002/docs"
	echo "  - ReDoc: http://localhost:8002/redoc"
	@echo "Press Ctrl+C to stop"
	@wait 