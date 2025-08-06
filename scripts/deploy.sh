#!/bin/bash

# Food Fast E-commerce Deployment Script
# Usage: ./deploy.sh [environment] [service]
# Example: ./deploy.sh staging api-gateway

set -e

ENVIRONMENT=${1:-staging}
SERVICE=${2:-all}
REGISTRY="ghcr.io"
REPO_NAME="truong20031456/food_and_fast_back-end"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Services configuration
declare -A SERVICES=(
    ["api-gateway"]="8000"
    ["auth-service"]="8001"
    ["user-service"]="8002"
    ["product-service"]="8003"
    ["payment-service"]="8005"
    ["order-service"]="8005"
    ["notification-service"]="8006"
    ["analytics-service"]="8007"
)

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
    exit 1
}

# Validate environment
validate_environment() {
    case $ENVIRONMENT in
        staging|production)
            log "Deploying to $ENVIRONMENT environment"
            ;;
        *)
            error "Invalid environment: $ENVIRONMENT. Use 'staging' or 'production'"
            ;;
    esac
}

# Get latest image tag
get_latest_tag() {
    local service=$1
    if [[ -n "$GITHUB_SHA" ]]; then
        echo "$GITHUB_SHA"
    else
        echo "latest"
    fi
}

# Deploy single service
deploy_service() {
    local service_name=$1
    local port=${SERVICES[$service_name]}
    
    if [[ -z "$port" ]]; then
        error "Unknown service: $service_name"
    fi
    
    local image_tag=$(get_latest_tag $service_name)
    local image_name="$REGISTRY/$REPO_NAME-$service_name:$image_tag"
    
    log "Deploying $service_name to $ENVIRONMENT"
    log "Image: $image_name"
    log "Port: $port"
    
    # For demonstration - replace with actual deployment commands
    case $ENVIRONMENT in
        staging)
            deploy_to_staging $service_name $image_name $port
            ;;
        production)
            deploy_to_production $service_name $image_name $port
            ;;
    esac
    
    success "$service_name deployed successfully"
}

# Deploy to staging environment
deploy_to_staging() {
    local service=$1
    local image=$2
    local port=$3
    
    log "Pulling latest image: $image"
    # docker pull $image
    
    log "Stopping existing container if running"
    # docker stop food-fast-${service}-staging || true
    # docker rm food-fast-${service}-staging || true
    
    log "Starting new container"
    # docker run -d \
    #   --name food-fast-${service}-staging \
    #   --network food-fast-staging \
    #   -p ${port}:${port} \
    #   -e ENVIRONMENT=staging \
    #   $image
    
    warning "Staging deployment commands are placeholder - implement actual deployment logic"
}

# Deploy to production environment
deploy_to_production() {
    local service=$1
    local image=$2
    local port=$3
    
    log "Production deployment for $service"
    
    # Health check before deployment
    log "Performing pre-deployment health checks"
    
    # Blue-green deployment example
    log "Implementing blue-green deployment"
    
    # Placeholder for actual production deployment
    # kubectl set image deployment/${service} ${service}=${image} -n production
    # helm upgrade ${service} ./helm/${service} --set image.tag=${GITHUB_SHA} -n production
    
    warning "Production deployment commands are placeholder - implement actual deployment logic"
}

# Health check function
health_check() {
    local service=$1
    local port=${SERVICES[$service]}
    local url="http://localhost:${port}/health"
    
    log "Performing health check for $service"
    
    for i in {1..30}; do
        if curl -f -s "$url" > /dev/null 2>&1; then
            success "Health check passed for $service"
            return 0
        fi
        log "Health check attempt $i/30 for $service"
        sleep 10
    done
    
    error "Health check failed for $service"
}

# Main deployment function
main() {
    log "Starting Food Fast E-commerce deployment"
    log "Environment: $ENVIRONMENT"
    log "Service: $SERVICE"
    
    validate_environment
    
    if [[ "$SERVICE" == "all" ]]; then
        log "Deploying all services"
        for service in "${!SERVICES[@]}"; do
            deploy_service "$service"
            # Uncomment for health checks
            # health_check "$service"
        done
    else
        deploy_service "$SERVICE"
        # Uncomment for health checks
        # health_check "$SERVICE"
    fi
    
    success "Deployment completed successfully!"
    
    # Post-deployment tasks
    log "Running post-deployment tasks"
    log "- Database migrations (if needed)"
    log "- Cache warming"
    log "- Monitoring alerts update"
    
    success "All deployment tasks completed!"
}

# Handle script interruption
trap 'error "Deployment interrupted"' INT TERM

# Check if running as source or executed
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi