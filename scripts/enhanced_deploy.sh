#!/bin/bash

# Enhanced Food Fast E-commerce Deployment Script
# Supports development, staging, and production environments
# Version: 2.0

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-staging}
SERVICE=${2:-all}
SKIP_TESTS=${3:-false}
REGISTRY="ghcr.io"
REPO_NAME="truong20031456/food_and_fast_back-end"
DEPLOY_TIMEOUT=600 # 10 minutes

# Service configuration with health check endpoints
declare -A SERVICES=(
    ["api-gateway"]="8000:/health"
    ["auth-service"]="8001:/health"
    ["user-service"]="8002:/health"
    ["product-service"]="8003:/health"
    ["order-service"]="8004:/health"
    ["payment-service"]="8005:/health"
    ["notification-service"]="8006:/health"
    ["analytics-service"]="8007:/health"
)

# Environment-specific configurations
declare -A ENV_CONFIGS=(
    ["development"]="docker-compose.dev.yml"
    ["staging"]="docker-compose.staging.yml"
    ["production"]="docker-compose.prod.yml"
)

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ⚠️  $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ❌ $1${NC}"
}

info() {
    echo -e "${CYAN}[$(date +'%Y-%m-%d %H:%M:%S')] ℹ️  $1${NC}"
}

# Progress indicator
show_progress() {
    local duration=$1
    local message=$2
    
    echo -n "$message"
    for ((i=0; i<duration; i++)); do
        echo -n "."
        sleep 1
    done
    echo " Done!"
}

# Validate environment
validate_environment() {
    log "Validating deployment environment: $ENVIRONMENT"
    
    if [[ ! "${!ENV_CONFIGS[@]}" =~ "$ENVIRONMENT" ]]; then
        error "Invalid environment: $ENVIRONMENT"
        error "Valid environments: ${!ENV_CONFIGS[@]}"
        exit 1
    fi
    
    # Check required tools
    local required_tools=("docker" "docker-compose" "git" "curl")
    
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            error "Required tool not found: $tool"
            exit 1
        fi
    done
    
    # Check Docker daemon
    if ! docker info &> /dev/null; then
        error "Docker daemon is not running"
        exit 1
    fi
    
    success "Environment validation passed"
}

# Pre-deployment checks
pre_deployment_checks() {
    log "Running pre-deployment checks..."
    
    # Check git status
    if [[ -n $(git status --porcelain) ]] && [[ "$ENVIRONMENT" == "production" ]]; then
        warning "Working directory has uncommitted changes"
        read -p "Continue with deployment? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            error "Deployment cancelled"
            exit 1
        fi
    fi
    
    # Check environment variables
    local required_env_vars=(
        "DATABASE_URL"
        "REDIS_URL"
        "JWT_SECRET_KEY"
        "SECRET_KEY"
    )
    
    for var in "${required_env_vars[@]}"; do
        if [[ -z "${!var}" ]] && [[ "$ENVIRONMENT" != "development" ]]; then
            warning "Environment variable $var is not set"
        fi
    done
    
    # Check disk space
    local available_space=$(df / | awk 'NR==2 {print $4}')
    local required_space=5000000 # 5GB in KB
    
    if [[ $available_space -lt $required_space ]]; then
        error "Insufficient disk space. Required: 5GB, Available: $((available_space/1024/1024))GB"
        exit 1
    fi
    
    success "Pre-deployment checks passed"
}

# Build Docker images
build_images() {
    local service=$1
    log "Building Docker images for: $service"
    
    if [[ "$service" == "all" ]]; then
        for svc in "${!SERVICES[@]}"; do
            build_single_image "$svc"
        done
    else
        build_single_image "$service"
    fi
    
    success "Image building completed"
}

build_single_image() {
    local service=$1
    local service_dir="${service//-/_}"
    
    if [[ ! -d "$service_dir" ]]; then
        warning "Service directory not found: $service_dir"
        return 1
    fi
    
    log "Building image for $service..."
    
    # Build with build args for different environments
    local build_args=""
    case "$ENVIRONMENT" in
        "production")
            build_args="--build-arg ENV=production --build-arg DEBUG=false"
            ;;
        "staging")
            build_args="--build-arg ENV=staging --build-arg DEBUG=false"
            ;;
        *)
            build_args="--build-arg ENV=development --build-arg DEBUG=true"
            ;;
    esac
    
    # Build image
    docker build $build_args \
        -t "$REGISTRY/$REPO_NAME/$service:$ENVIRONMENT" \
        -t "$REGISTRY/$REPO_NAME/$service:latest" \
        "$service_dir/"
    
    if [[ $? -eq 0 ]]; then
        success "✅ Built image for $service"
    else
        error "❌ Failed to build image for $service"
        exit 1
    fi
}

# Run tests
run_tests() {
    if [[ "$SKIP_TESTS" == "true" ]]; then
        warning "Skipping tests as requested"
        return 0
    fi
    
    log "Running test suite..."
    
    # Unit tests
    log "Running unit tests..."
    for service in "${!SERVICES[@]}"; do
        local service_dir="${service//-/_}"
        
        if [[ -f "$service_dir/pytest.ini" ]] || [[ -d "$service_dir/tests" ]]; then
            log "Running tests for $service..."
            
            cd "$service_dir"
            if command -v pytest &> /dev/null; then
                pytest -v --tb=short
                if [[ $? -ne 0 ]]; then
                    error "Unit tests failed for $service"
                    exit 1
                fi
            else
                warning "pytest not found, skipping tests for $service"
            fi
            cd ..
        fi
    done
    
    # Integration tests
    if [[ -f "tests/integration_tests.py" ]]; then
        log "Running integration tests..."
        python tests/integration_tests.py
        if [[ $? -ne 0 ]] && [[ "$ENVIRONMENT" == "production" ]]; then
            error "Integration tests failed"
            exit 1
        fi
    fi
    
    success "All tests passed"
}

# Security scan
security_scan() {
    log "Running security scans..."
    
    # Scan Docker images for vulnerabilities (if trivy is available)
    if command -v trivy &> /dev/null; then
        for service in "${!SERVICES[@]}"; do
            log "Scanning $service for vulnerabilities..."
            trivy image --severity HIGH,CRITICAL "$REGISTRY/$REPO_NAME/$service:$ENVIRONMENT"
            
            if [[ $? -ne 0 ]] && [[ "$ENVIRONMENT" == "production" ]]; then
                warning "Security vulnerabilities found in $service"
                read -p "Continue deployment? (y/N): " -n 1 -r
                echo
                if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                    error "Deployment cancelled due to security concerns"
                    exit 1
                fi
            fi
        done
    else
        warning "Trivy not installed, skipping vulnerability scan"
    fi
    
    # Check for secrets in code
    if command -v gitleaks &> /dev/null; then
        log "Scanning for secrets..."
        gitleaks detect --source . --verbose
        if [[ $? -ne 0 ]] && [[ "$ENVIRONMENT" == "production" ]]; then
            error "Potential secrets detected in code"
            exit 1
        fi
    fi
    
    success "Security scan completed"
}

# Deploy services
deploy_services() {
    local service=$1
    log "Deploying services to $ENVIRONMENT environment"
    
    # Prepare environment file
    prepare_environment_file
    
    # Get the appropriate docker-compose file
    local compose_file=${ENV_CONFIGS[$ENVIRONMENT]}
    
    if [[ ! -f "$compose_file" ]]; then
        warning "Compose file not found: $compose_file, using docker-compose.yml"
        compose_file="docker-compose.yml"
    fi
    
    # Deploy infrastructure first
    log "Starting infrastructure services..."
    docker-compose -f "$compose_file" up -d postgres redis
    
    # Wait for infrastructure to be ready
    wait_for_infrastructure
    
    # Deploy application services
    if [[ "$service" == "all" ]]; then
        log "Deploying all services..."
        docker-compose -f "$compose_file" up -d
    else
        log "Deploying $service..."
        docker-compose -f "$compose_file" up -d "$service"
    fi
    
    success "Services deployed successfully"
}

prepare_environment_file() {
    log "Preparing environment configuration..."
    
    # Copy environment template
    if [[ -f ".env.$ENVIRONMENT" ]]; then
        cp ".env.$ENVIRONMENT" ".env"
        success "Environment configuration loaded for $ENVIRONMENT"
    elif [[ -f "shared_code/env.example" ]]; then
        cp "shared_code/env.example" ".env"
        warning "Using example environment file - update with actual values"
    else
        warning "No environment file found"
    fi
}

wait_for_infrastructure() {
    log "Waiting for infrastructure services..."
    
    # Wait for PostgreSQL
    info "Waiting for PostgreSQL..."
    for i in {1..30}; do
        if docker exec food_fast_postgres pg_isready -U postgres &> /dev/null; then
            success "PostgreSQL is ready"
            break
        fi
        if [[ $i -eq 30 ]]; then
            error "PostgreSQL failed to start"
            exit 1
        fi
        sleep 2
    done
    
    # Wait for Redis
    info "Waiting for Redis..."
    for i in {1..30}; do
        if docker exec food_fast_redis redis-cli ping &> /dev/null; then
            success "Redis is ready"
            break
        fi
        if [[ $i -eq 30 ]]; then
            error "Redis failed to start"
            exit 1
        fi
        sleep 2
    done
}

# Health checks
health_check() {
    local service=$1
    local port_endpoint=${SERVICES[$service]}
    local port=$(echo $port_endpoint | cut -d':' -f1)
    local endpoint=$(echo $port_endpoint | cut -d':' -f2)
    local url="http://localhost:${port}${endpoint}"
    
    log "Performing health check for $service"
    
    local max_attempts=60
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        if curl -f -s "$url" > /dev/null 2>&1; then
            success "Health check passed for $service ($attempt/$max_attempts)"
            return 0
        fi
        
        if [[ $((attempt % 10)) -eq 0 ]]; then
            info "Health check attempt $attempt/$max_attempts for $service"
        fi
        
        sleep 5
        ((attempt++))
    done
    
    error "Health check failed for $service after $max_attempts attempts"
    return 1
}

# Performance check
performance_check() {
    log "Running performance checks..."
    
    # Check API Gateway response time
    local gateway_url="http://localhost:8000/health"
    local response_time=$(curl -o /dev/null -s -w "%{time_total}" "$gateway_url" 2>/dev/null || echo "0")
    
    if (( $(echo "$response_time > 2.0" | bc -l) )); then
        warning "API Gateway response time is high: ${response_time}s"
    else
        success "API Gateway response time: ${response_time}s"
    fi
    
    # Check memory usage
    local memory_usage=$(docker stats --no-stream --format "table {{.Container}}\t{{.MemUsage}}" | grep -E "(api|auth|user|product|order|payment|notification|analytics)")
    info "Memory usage:"
    echo "$memory_usage"
    
    success "Performance check completed"
}

# Rollback function
rollback() {
    log "Rolling back deployment..."
    
    # Stop current containers
    docker-compose down
    
    # Pull previous version (if available)
    # This is a simplified rollback - in production, you'd have proper versioning
    warning "Rollback functionality is basic - implement proper versioning for production"
    
    error "Deployment failed - manual intervention may be required"
}

# Cleanup function
cleanup() {
    log "Cleaning up..."
    
    # Remove dangling images
    docker image prune -f
    
    # Remove unused volumes (be careful in production)
    if [[ "$ENVIRONMENT" != "production" ]]; then
        docker volume prune -f
    fi
    
    success "Cleanup completed"
}

# Monitoring setup
setup_monitoring() {
    log "Setting up monitoring..."
    
    # Start monitoring stack if in infrastructure directory
    if [[ -d "infrastructure/monitoring" ]]; then
        cd infrastructure/monitoring
        docker-compose up -d
        cd ../..
        success "Monitoring stack started"
    else
        warning "Monitoring configuration not found"
    fi
    
    # Verify monitoring endpoints
    local monitoring_endpoints=(
        "http://localhost:9090"  # Prometheus
        "http://localhost:3000"  # Grafana
    )
    
    for endpoint in "${monitoring_endpoints[@]}"; do
        if curl -f -s "$endpoint" > /dev/null 2>&1; then
            success "Monitoring endpoint available: $endpoint"
        else
            warning "Monitoring endpoint not available: $endpoint"
        fi
    done
}

# Main deployment workflow
main() {
    log "🚀 Starting Food Fast E-commerce deployment"
    log "Environment: $ENVIRONMENT"
    log "Service: $SERVICE"
    log "Skip tests: $SKIP_TESTS"
    echo
    
    # Trap errors for cleanup
    trap 'error "Deployment failed"; rollback; exit 1' ERR
    
    # Validation phase
    validate_environment
    pre_deployment_checks
    
    # Build phase
    build_images "$SERVICE"
    
    # Test phase
    run_tests
    
    # Security phase
    security_scan
    
    # Deploy phase
    deploy_services "$SERVICE"
    
    # Verification phase
    if [[ "$SERVICE" == "all" ]]; then
        for service in "${!SERVICES[@]}"; do
            health_check "$service" || {
                error "Deployment verification failed for $service"
                rollback
                exit 1
            }
        done
    else
        health_check "$SERVICE" || {
            error "Deployment verification failed for $SERVICE"
            rollback
            exit 1
        }
    fi
    
    # Performance verification
    performance_check
    
    # Setup monitoring (for staging/production)
    if [[ "$ENVIRONMENT" != "development" ]]; then
        setup_monitoring
    fi
    
    # Cleanup
    cleanup
    
    # Success message
    echo
    success "🎉 Deployment completed successfully!"
    success "Environment: $ENVIRONMENT"
    success "Services deployed: $SERVICE"
    
    # Show useful URLs
    echo
    info "📊 Service URLs:"
    for service in "${!SERVICES[@]}"; do
        local port=$(echo ${SERVICES[$service]} | cut -d':' -f1)
        info "  $service: http://localhost:$port"
    done
    
    if [[ "$ENVIRONMENT" != "development" ]]; then
        echo
        info "📈 Monitoring URLs:"
        info "  Prometheus: http://localhost:9090"
        info "  Grafana: http://localhost:3000 (admin/admin)"
    fi
    
    echo
    success "Deployment completed in $(date)"
}

# Show help
show_help() {
    echo "Food Fast E-commerce Deployment Script"
    echo "Usage: $0 [environment] [service] [skip_tests]"
    echo
    echo "Parameters:"
    echo "  environment  : development, staging, production (default: staging)"
    echo "  service      : service name or 'all' (default: all)"
    echo "  skip_tests   : true/false (default: false)"
    echo
    echo "Examples:"
    echo "  $0                           # Deploy all services to staging"
    echo "  $0 production               # Deploy all services to production"
    echo "  $0 staging api-gateway      # Deploy only API gateway to staging"
    echo "  $0 development all true     # Deploy to development, skip tests"
    echo
    echo "Available services:"
    for service in "${!SERVICES[@]}"; do
        echo "  - $service"
    done
}

# Parse command line arguments
case "${1:-}" in
    "-h"|"--help"|"help")
        show_help
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac
