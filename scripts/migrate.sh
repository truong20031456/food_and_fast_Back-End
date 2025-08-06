#!/bin/bash

# Database Migration Automation Script
# Food Fast E-commerce - Production-Ready Migrations

set -e

ENVIRONMENT=${1:-development}
SERVICE=${2:-all}
ACTION=${3:-migrate}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Services with database migrations
declare -A MIGRATION_SERVICES=(
    ["auth-service"]="auth_service"
    ["user-service"]="user_service"
    ["product-service"]="product_service"
    ["order-service"]="order_service"
    ["payment-service"]="payment_service"
    ["notification-service"]="notification_service"
    ["analytics-service"]="analytics_service"
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

# Load environment variables
load_environment() {
    local env_file=".env.${ENVIRONMENT}"
    
    if [[ ! -f "$env_file" ]]; then
        error "Environment file $env_file not found"
    fi
    
    log "Loading environment from $env_file"
    export $(grep -v '^#' "$env_file" | xargs)
}

# Check database connectivity
check_database_connection() {
    log "Checking database connectivity..."
    
    local max_attempts=30
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        if PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d $POSTGRES_DB -c "SELECT 1;" > /dev/null 2>&1; then
            success "Database connection established"
            return 0
        fi
        
        log "Database connection attempt $attempt/$max_attempts failed, retrying in 5 seconds..."
        sleep 5
        ((attempt++))
    done
    
    error "Failed to connect to database after $max_attempts attempts"
}

# Create database backup
create_backup() {
    local service_name=$1
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local backup_dir="./backups/${ENVIRONMENT}"
    local backup_file="${backup_dir}/${service_name}_${timestamp}.sql"
    
    mkdir -p "$backup_dir"
    
    log "Creating backup for $service_name"
    
    PGPASSWORD=$POSTGRES_PASSWORD pg_dump \
        -h $POSTGRES_HOST \
        -p $POSTGRES_PORT \
        -U $POSTGRES_USER \
        -d $POSTGRES_DB \
        --schema="${service_name}" \
        --file="$backup_file" \
        --verbose
    
    if [[ -f "$backup_file" ]]; then
        success "Backup created: $backup_file"
        
        # Compress backup
        gzip "$backup_file"
        success "Backup compressed: ${backup_file}.gz"
        
        # Clean old backups (keep last 10)
        find "$backup_dir" -name "${service_name}_*.sql.gz" -type f | sort -r | tail -n +11 | xargs rm -f
        log "Old backups cleaned up"
    else
        error "Failed to create backup for $service_name"
    fi
}

# Run Alembic migrations for a service
run_service_migration() {
    local service_name=$1
    local service_dir=${MIGRATION_SERVICES[$service_name]}
    
    if [[ ! -d "$service_dir" ]]; then
        error "Service directory $service_dir not found"
    fi
    
    log "Running migrations for $service_name"
    
    cd "$service_dir"
    
    # Check if alembic is configured
    if [[ ! -f "alembic.ini" ]]; then
        warning "No alembic.ini found for $service_name, skipping migrations"
        cd ..
        return 0
    fi
    
    # Set database URL for this service
    export DATABASE_URL="postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}"
    
    case $ACTION in
        "migrate")
            log "Applying migrations for $service_name"
            alembic upgrade head
            success "Migrations applied for $service_name"
            ;;
        "rollback")
            log "Rolling back last migration for $service_name"
            alembic downgrade -1
            success "Rollback completed for $service_name"
            ;;
        "status")
            log "Checking migration status for $service_name"
            alembic current
            alembic show head
            ;;
        "history")
            log "Showing migration history for $service_name"
            alembic history --verbose
            ;;
        "generate")
            if [[ -z "$4" ]]; then
                error "Migration message required for generate action"
            fi
            log "Generating new migration for $service_name: $4"
            alembic revision --autogenerate -m "$4"
            success "Migration generated for $service_name"
            ;;
        *)
            error "Unknown action: $ACTION"
            ;;
    esac
    
    cd ..
}

# Run migrations for all services
run_all_migrations() {
    log "Running migrations for all services"
    
    for service in "${!MIGRATION_SERVICES[@]}"; do
        if [[ "$ACTION" == "migrate" ]]; then
            create_backup "$service"
        fi
        run_service_migration "$service"
    done
}

# Validate migration environment
validate_environment() {
    if [[ "$ENVIRONMENT" == "production" ]]; then
        warning "You are about to run migrations in PRODUCTION environment"
        read -p "Are you sure you want to continue? (yes/no): " confirm
        
        if [[ "$confirm" != "yes" ]]; then
            log "Migration cancelled by user"
            exit 0
        fi
        
        # Additional production safeguards
        if [[ "$ACTION" == "migrate" ]]; then
            log "Creating full database backup before production migration..."
            create_full_backup
        fi
    fi
}

# Create full database backup (production only)
create_full_backup() {
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local backup_dir="./backups/${ENVIRONMENT}/full"
    local backup_file="${backup_dir}/full_backup_${timestamp}.sql"
    
    mkdir -p "$backup_dir"
    
    log "Creating full database backup"
    
    PGPASSWORD=$POSTGRES_PASSWORD pg_dump \
        -h $POSTGRES_HOST \
        -p $POSTGRES_PORT \
        -U $POSTGRES_USER \
        -d $POSTGRES_DB \
        --file="$backup_file" \
        --verbose
    
    gzip "$backup_file"
    success "Full backup created: ${backup_file}.gz"
}

# Migration health check
migration_health_check() {
    log "Performing post-migration health check"
    
    for service in "${!MIGRATION_SERVICES[@]}"; do
        local service_dir=${MIGRATION_SERVICES[$service]}
        
        cd "$service_dir"
        
        # Check if migrations are up to date
        local current_rev=$(alembic current | cut -d' ' -f1)
        local head_rev=$(alembic show head | cut -d' ' -f1)
        
        if [[ "$current_rev" == "$head_rev" ]]; then
            success "$service migrations are up to date"
        else
            error "$service migrations are NOT up to date (current: $current_rev, head: $head_rev)"
        fi
        
        cd ..
    done
}

# Show usage information
show_usage() {
    echo "Usage: $0 [environment] [service] [action] [message]"
    echo ""
    echo "Environments: development, staging, production"
    echo "Services: all, auth-service, user-service, product-service, order-service, payment-service, notification-service, analytics-service"
    echo "Actions: migrate, rollback, status, history, generate"
    echo ""
    echo "Examples:"
    echo "  $0 development all migrate                    # Run all migrations in development"
    echo "  $0 production auth-service migrate            # Run auth service migrations in production"
    echo "  $0 staging all status                         # Check migration status for all services"
    echo "  $0 development user-service generate 'Add user preferences'  # Generate new migration"
    echo ""
}

# Main function
main() {
    if [[ "$1" == "--help" || "$1" == "-h" ]]; then
        show_usage
        exit 0
    fi
    
    log "Food Fast E-commerce Database Migration Tool"
    log "Environment: $ENVIRONMENT"
    log "Service: $SERVICE"
    log "Action: $ACTION"
    
    validate_environment
    load_environment
    check_database_connection
    
    if [[ "$SERVICE" == "all" ]]; then
        run_all_migrations
    else
        if [[ -z "${MIGRATION_SERVICES[$SERVICE]}" ]]; then
            error "Unknown service: $SERVICE"
        fi
        
        if [[ "$ACTION" == "migrate" ]]; then
            create_backup "$SERVICE"
        fi
        run_service_migration "$SERVICE" "$4"
    fi
    
    if [[ "$ACTION" == "migrate" ]]; then
        migration_health_check
    fi
    
    success "Migration operation completed successfully!"
}

# Handle script interruption
trap 'error "Migration interrupted"' INT TERM

# Check if running as source or executed
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
