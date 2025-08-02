#!/bin/bash

# User Service Deployment Script
# Usage: ./scripts/deploy.sh [environment] [version]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
ENVIRONMENT=${1:-staging}
VERSION=${2:-latest}
REGISTRY="ghcr.io"
IMAGE_NAME="your-username/user-service"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        exit 1
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check if kubectl is installed (for Kubernetes deployment)
    if ! command -v kubectl &> /dev/null; then
        print_warning "kubectl is not installed - Kubernetes deployment will be skipped"
    fi
    
    print_success "Prerequisites check completed"
}

# Function to build Docker image
build_image() {
    print_status "Building Docker image..."
    
    docker build -t ${REGISTRY}/${IMAGE_NAME}:${VERSION} .
    docker tag ${REGISTRY}/${IMAGE_NAME}:${VERSION} ${REGISTRY}/${IMAGE_NAME}:latest
    
    print_success "Docker image built successfully"
}

# Function to push Docker image
push_image() {
    print_status "Pushing Docker image to registry..."
    
    docker push ${REGISTRY}/${IMAGE_NAME}:${VERSION}
    docker push ${REGISTRY}/${IMAGE_NAME}:latest
    
    print_success "Docker image pushed successfully"
}

# Function to deploy to Docker Compose
deploy_docker_compose() {
    print_status "Deploying with Docker Compose..."
    
    # Stop existing containers
    docker-compose down
    
    # Pull latest images
    docker-compose pull
    
    # Start services
    if [ "$ENVIRONMENT" = "production" ]; then
        docker-compose --profile production up -d
    else
        docker-compose up -d
    fi
    
    print_success "Docker Compose deployment completed"
}

# Function to deploy to Kubernetes
deploy_kubernetes() {
    if ! command -v kubectl &> /dev/null; then
        print_warning "Skipping Kubernetes deployment - kubectl not available"
        return
    fi
    
    print_status "Deploying to Kubernetes..."
    
    # Update image tag in deployment
    sed -i "s|image: .*|image: ${REGISTRY}/${IMAGE_NAME}:${VERSION}|g" k8s/deployment.yaml
    
    # Apply Kubernetes manifests
    kubectl apply -f k8s/
    
    # Wait for deployment to be ready
    kubectl rollout status deployment/user-service
    
    print_success "Kubernetes deployment completed"
}

# Function to run health checks
health_check() {
    print_status "Running health checks..."
    
    # Wait for service to be ready
    sleep 10
    
    # Check health endpoint
    if curl -f http://localhost:8002/health > /dev/null 2>&1; then
        print_success "Health check passed"
    else
        print_error "Health check failed"
        exit 1
    fi
}

# Function to show deployment info
show_deployment_info() {
    print_status "Deployment Information:"
    echo "  Environment: $ENVIRONMENT"
    echo "  Version: $VERSION"
    echo "  Image: ${REGISTRY}/${IMAGE_NAME}:${VERSION}"
    echo "  Health Check: http://localhost:8002/health"
    echo "  API Docs: http://localhost:8002/docs"
}

# Main deployment function
main() {
    print_status "Starting deployment for environment: $ENVIRONMENT, version: $VERSION"
    
    check_prerequisites
    build_image
    push_image
    
    case $ENVIRONMENT in
        "local"|"development")
            deploy_docker_compose
            ;;
        "staging"|"production")
            deploy_docker_compose
            deploy_kubernetes
            ;;
        *)
            print_error "Unknown environment: $ENVIRONMENT"
            print_status "Available environments: local, development, staging, production"
            exit 1
            ;;
    esac
    
    health_check
    show_deployment_info
    
    print_success "Deployment completed successfully!"
}

# Run main function
main "$@" 