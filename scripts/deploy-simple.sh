#!/bin/bash

# Food Fast E-commerce Deployment Script
# Simple, unified deployment for all environments

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-development}
PROJECT_NAME="food-fast-ecommerce"

echo -e "${BLUE}🚀 Food Fast E-commerce Deployment${NC}"
echo -e "${BLUE}Environment: ${ENVIRONMENT}${NC}"
echo -e "${BLUE}========================================${NC}"

# Function to print status
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed"
        exit 1
    fi
    
    print_status "Prerequisites check passed"
}

# Choose compose file based on environment
get_compose_file() {
    case $ENVIRONMENT in
        "production"|"prod")
            echo "docker-compose.prod.yml"
            ;;
        "staging")
            echo "docker-compose.staging.yml"
            ;;
        "development"|"dev"|*)
            echo "docker-compose.yml"
            ;;
    esac
}

# Deploy function
deploy() {
    local compose_file=$(get_compose_file)
    
    print_status "Using compose file: $compose_file"
    
    # Check if compose file exists
    if [ ! -f "$compose_file" ]; then
        print_error "Compose file $compose_file not found"
        exit 1
    fi
    
    # Create environment file if it doesn't exist
    if [ ! -f ".env" ]; then
        print_warning "No .env file found, creating from .env.example"
        cp .env.example .env
        print_warning "Please update .env file with your configuration"
    fi
    
    # Stop existing containers
    print_status "Stopping existing containers..."
    docker-compose -f $compose_file down || true
    
    # Pull latest images (for production)
    if [ "$ENVIRONMENT" = "production" ] || [ "$ENVIRONMENT" = "prod" ]; then
        print_status "Pulling latest images..."
        docker-compose -f $compose_file pull
    fi
    
    # Build and start services
    print_status "Building and starting services..."
    docker-compose -f $compose_file up -d --build
    
    # Wait for services to be ready
    print_status "Waiting for services to be ready..."
    sleep 30
    
    # Run health checks
    health_check
}

# Health check function
health_check() {
    print_status "Running health checks..."
    
    local services=("api_gateway:8000" "auth_service:8001" "user_service:8002" "product_service:8003" "order_service:8004" "payment_service:8005" "notification_service:8006" "analytics_service:8007")
    
    for service_port in "${services[@]}"; do
        IFS=':' read -r service port <<< "$service_port"
        
        if curl -sf "http://localhost:$port/health" > /dev/null; then
            print_status "$service is healthy"
        else
            print_warning "$service health check failed (might still be starting)"
        fi
    done
}

# Rollback function
rollback() {
    print_status "Rolling back deployment..."
    local compose_file=$(get_compose_file)
    
    docker-compose -f $compose_file down
    
    # Here you could implement more sophisticated rollback logic
    # For example, using previous image tags
    
    print_status "Rollback completed"
}

# Main execution
case "${2:-deploy}" in
    "deploy")
        check_prerequisites
        deploy
        print_status "🎉 Deployment completed successfully!"
        print_status "Services are available at:"
        echo "  - API Gateway: http://localhost:8000"
        echo "  - Auth Service: http://localhost:8001"
        echo "  - User Service: http://localhost:8002"
        echo "  - Product Service: http://localhost:8003"
        echo "  - Order Service: http://localhost:8004"
        echo "  - Payment Service: http://localhost:8005"
        echo "  - Notification Service: http://localhost:8006"
        echo "  - Analytics Service: http://localhost:8007"
        ;;
    "rollback")
        rollback
        ;;
    "health")
        health_check
        ;;
    *)
        echo "Usage: $0 [environment] [action]"
        echo "  environment: development|staging|production (default: development)"
        echo "  action: deploy|rollback|health (default: deploy)"
        echo ""
        echo "Examples:"
        echo "  $0 development deploy"
        echo "  $0 production deploy"
        echo "  $0 staging rollback"
        echo "  $0 development health"
        exit 1
        ;;
esac
