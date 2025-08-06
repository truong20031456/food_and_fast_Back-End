#!/bin/bash

# Health Check Script for Food Fast E-commerce Services
# Usage: ./health-check.sh [environment] [service]

set -e

ENVIRONMENT=${1:-staging}
SERVICE=${2:-all}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Service endpoints
declare -A SERVICE_URLS=(
    ["api-gateway"]="http://localhost:8000"
    ["auth-service"]="http://localhost:8001"
    ["user-service"]="http://localhost:8002"
    ["product-service"]="http://localhost:8003"
    ["payment-service"]="http://localhost:8005"
    ["order-service"]="http://localhost:8005"
    ["notification-service"]="http://localhost:8006"
    ["analytics-service"]="http://localhost:8007"
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
}

# Check single service health
check_service_health() {
    local service_name=$1
    local base_url=${SERVICE_URLS[$service_name]}
    
    if [[ -z "$base_url" ]]; then
        error "Unknown service: $service_name"
        return 1
    fi
    
    log "Checking health for $service_name"
    
    # Try multiple health endpoints
    local endpoints=("/health" "/healthz" "/ping" "/")
    local healthy=false
    
    for endpoint in "${endpoints[@]}"; do
        local url="${base_url}${endpoint}"
        log "Testing endpoint: $url"
        
        if curl -f -s -m 10 "$url" > /dev/null 2>&1; then
            success "$service_name is healthy (endpoint: $endpoint)"
            healthy=true
            break
        fi
    done
    
    if [[ "$healthy" == "false" ]]; then
        error "$service_name is not responding to health checks"
        return 1
    fi
    
    return 0
}

# Check infrastructure services
check_infrastructure() {
    log "Checking infrastructure services"
    
    # PostgreSQL
    if pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
        success "PostgreSQL is ready"
    else
        warning "PostgreSQL is not ready"
    fi
    
    # Redis
    if redis-cli -h localhost ping > /dev/null 2>&1; then
        success "Redis is ready"
    else
        warning "Redis is not ready"
    fi
    
    # Elasticsearch (if available)
    if curl -f -s http://localhost:9200/_cluster/health > /dev/null 2>&1; then
        success "Elasticsearch is ready"
    else
        warning "Elasticsearch is not ready"
    fi
    
    # RabbitMQ (if available)
    if curl -f -s http://localhost:15672 > /dev/null 2>&1; then
        success "RabbitMQ management is ready"
    else
        warning "RabbitMQ management is not ready"
    fi
}

# Main health check function
main() {
    log "Starting Food Fast E-commerce health check"
    log "Environment: $ENVIRONMENT"
    log "Service: $SERVICE"
    
    # Check infrastructure first
    check_infrastructure
    
    local failed_services=()
    
    if [[ "$SERVICE" == "all" ]]; then
        log "Checking all services"
        for service in "${!SERVICE_URLS[@]}"; do
            if ! check_service_health "$service"; then
                failed_services+=("$service")
            fi
        done
    else
        if ! check_service_health "$SERVICE"; then
            failed_services+=("$SERVICE")
        fi
    fi
    
    # Summary
    if [[ ${#failed_services[@]} -eq 0 ]]; then
        success "All health checks passed!"
        exit 0
    else
        error "Health checks failed for: ${failed_services[*]}"
        exit 1
    fi
}

# Handle script interruption
trap 'error "Health check interrupted"' INT TERM

# Execute main function
main "$@"