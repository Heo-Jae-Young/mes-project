#!/bin/bash

# MES Production Deployment Script
# Usage: ./scripts/deploy.sh [--ssl] [--backup]

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="mes-production"
BACKUP_DIR="./backups"
SSL_ENABLED=false
BACKUP_ENABLED=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --ssl)
            SSL_ENABLED=true
            shift
            ;;
        --backup)
            BACKUP_ENABLED=true
            shift
            ;;
        --help)
            echo "Usage: $0 [--ssl] [--backup]"
            echo "  --ssl: Enable SSL certificate generation"
            echo "  --backup: Create database backup before deployment"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

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

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        exit 1
    fi
    
    if ! docker compose version &> /dev/null; then
        print_error "Docker Compose plugin is not installed"
        exit 1
    fi
    
    if [[ ! -f ".env.prod" ]]; then
        print_error ".env.prod file not found"
        print_warning "Please copy .env.prod.example to .env.prod and configure it"
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

# Create backup
create_backup() {
    if [[ "$BACKUP_ENABLED" == true ]]; then
        print_status "Creating database backup..."
        
        mkdir -p "$BACKUP_DIR"
        timestamp=$(date +"%Y%m%d_%H%M%S")
        backup_file="$BACKUP_DIR/mes_backup_$timestamp.sql"
        
        if docker compose -f docker-compose.prod.yml --env-file .env.prod exec -T db mysqldump \
            --user="$DB_USER" \
            --password="$DB_PASSWORD" \
            --host=localhost \
            --single-transaction \
            --routines \
            --triggers \
            "$DB_NAME" > "$backup_file"; then
            print_success "Backup created: $backup_file"
        else
            print_warning "Backup failed, but continuing with deployment"
        fi
    fi
}

# Build and deploy
deploy() {
    print_status "Starting deployment..."
    
    # Load environment variables
    export $(grep -v '^#' .env.prod | xargs)
    
    # Build images
    print_status "Building Docker images..."
    docker compose -f docker-compose.prod.yml --env-file .env.prod build --no-cache
    
    # Start services
    print_status "Starting services..."
    docker compose -f docker-compose.prod.yml --env-file .env.prod up -d
    
    # Wait for database to be ready
    print_status "Waiting for database to be ready..."
    sleep 30
    
    # Run migrations
    print_status "Running database migrations..."
    docker compose -f docker-compose.prod.yml --env-file .env.prod exec -T backend python manage.py migrate
    
    # Collect static files
    print_status "Collecting static files..."
    docker compose -f docker-compose.prod.yml --env-file .env.prod exec -T backend python manage.py collectstatic --noinput
    
    # Create superuser if it doesn't exist
    print_status "Setting up admin user..."
    docker compose -f docker-compose.prod.yml --env-file .env.prod exec -T backend python manage.py shell << 'EOF'
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print("Admin user created: admin/admin123")
else:
    print("Admin user already exists")
EOF
    
    print_success "Deployment completed successfully!"
}

# Setup SSL certificates
setup_ssl() {
    if [[ "$SSL_ENABLED" == true ]]; then
        print_status "Setting up SSL certificates..."
        
        if [[ -z "$DOMAIN_NAME" ]] || [[ -z "$SSL_EMAIL" ]]; then
            print_error "DOMAIN_NAME and SSL_EMAIL must be set in .env.prod for SSL setup"
            exit 1
        fi
        
        # Generate certificates using certbot
        docker compose -f docker-compose.prod.yml --env-file .env.prod run --rm certbot \
            certonly \
            --webroot \
            --webroot-path /var/www/certbot \
            --email "$SSL_EMAIL" \
            --agree-tos \
            --no-eff-email \
            -d "$DOMAIN_NAME"
        
        # Reload nginx with new certificates
        docker compose -f docker-compose.prod.yml --env-file .env.prod restart nginx
        
        print_success "SSL certificates configured"
    fi
}

# Health check
health_check() {
    print_status "Running health checks..."
    
    # Check if services are running
    if docker compose -f docker-compose.prod.yml --env-file .env.prod ps | grep -q "Up"; then
        print_success "Services are running"
    else
        print_error "Some services are not running"
        docker compose -f docker-compose.prod.yml --env-file .env.prod ps
        exit 1
    fi
    
    # Check backend health
    sleep 10
    if curl -f http://localhost/health &> /dev/null; then
        print_success "Backend health check passed"
    else
        print_warning "Backend health check failed"
    fi
    
    # Display service status
    print_status "Service status:"
    docker compose -f docker-compose.prod.yml --env-file .env.prod ps
}

# Main execution
main() {
    print_status "🚀 Starting MES Production Deployment"
    
    check_prerequisites
    create_backup
    deploy
    setup_ssl
    health_check
    
    print_success "🎉 Deployment completed successfully!"
    print_status "Access your application at: http://$(curl -s ifconfig.me)"
    print_status "Admin panel: http://$(curl -s ifconfig.me)/admin"
    print_status "Default admin credentials: admin/admin123"
    print_warning "⚠️  Please change the default admin password immediately!"
}

# Run main function
main "$@"