#!/bin/bash

# 4-Plex Unified Investment Platform Startup Script
# Combines foreclosure discovery with professional investment analysis

set -e  # Exit on any error

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_FILE="$PROJECT_DIR/logs/startup.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging function
log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${timestamp} [${level}] ${message}" | tee -a "$LOG_FILE"
}

info() {
    log "INFO" "${BLUE}$@${NC}"
}

success() {
    log "SUCCESS" "${GREEN}$@${NC}"
}

warning() {
    log "WARNING" "${YELLOW}$@${NC}"
}

error() {
    log "ERROR" "${RED}$@${NC}"
}

# Banner
show_banner() {
    echo -e "${PURPLE}"
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║              🏘️  4-Plex Unified Investment Platform            ║"
    echo "║                                                                ║"
    echo "║     AI-Powered Property Discovery + Professional Analysis      ║"
    echo "║                                                                ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Check prerequisites
check_prerequisites() {
    info "🔍 Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if Docker is running
    if ! docker info &> /dev/null; then
        error "Docker is not running. Please start Docker first."
        exit 1
    fi
    
    success "✅ Prerequisites check passed"
}

# Setup environment
setup_environment() {
    info "⚙️  Setting up environment..."
    
    # Create directories
    mkdir -p "$PROJECT_DIR"/{data/{discovery,valuation,documents,exports,logs},logs,config,monitoring}
    
    # Check if .env file exists
    if [[ ! -f "$PROJECT_DIR/.env" ]]; then
        if [[ -f "$PROJECT_DIR/.env.example" ]]; then
            warning "⚠️  No .env file found. Creating from .env.example..."
            cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
            warning "📝 Please edit .env file with your API keys before continuing."
            warning "   Required: OPENAI_API_KEY, database passwords"
            
            # Check if running interactively
            if [[ -t 0 ]]; then
                echo -e "${YELLOW}Would you like to edit the .env file now? (y/n)${NC}"
                read -r response
                if [[ "$response" =~ ^[Yy]$ ]]; then
                    ${EDITOR:-nano} "$PROJECT_DIR/.env"
                fi
            else
                warning "Running in non-interactive mode. Please configure .env manually."
                exit 1
            fi
        else
            error "No .env.example file found. Cannot create environment configuration."
            exit 1
        fi
    fi
    
    # Source environment variables
    source "$PROJECT_DIR/.env"
    
    success "✅ Environment setup completed"
}

# Pull/build Docker images
prepare_images() {
    info "🐳 Preparing Docker images..."
    
    cd "$PROJECT_DIR"
    
    # Pull base images
    info "📥 Pulling base images..."
    docker-compose pull postgres redis neo4j prometheus grafana nginx 2>/dev/null || true
    
    # Build custom images
    info "🔨 Building application images..."
    docker-compose build --no-cache
    
    success "✅ Docker images prepared"
}

# Initialize databases
initialize_databases() {
    info "🗄️  Initializing databases..."
    
    cd "$PROJECT_DIR"
    
    # Start database services first
    info "Starting database services..."
    docker-compose up -d postgres redis neo4j
    
    # Wait for databases to be ready
    info "⏳ Waiting for databases to be ready..."
    sleep 30
    
    # Check PostgreSQL
    local max_attempts=30
    local attempt=0
    while ! docker-compose exec -T postgres pg_isready -U postgres -d unified_properties &> /dev/null; do
        attempt=$((attempt + 1))
        if [[ $attempt -ge $max_attempts ]]; then
            error "PostgreSQL failed to start after ${max_attempts} attempts"
            exit 1
        fi
        sleep 2
    done
    
    # Check Redis
    attempt=0
    while ! docker-compose exec -T redis redis-cli ping &> /dev/null; do
        attempt=$((attempt + 1))
        if [[ $attempt -ge $max_attempts ]]; then
            error "Redis failed to start after ${max_attempts} attempts"
            exit 1
        fi
        sleep 2
    done
    
    # Check Neo4j
    attempt=0
    while ! docker-compose exec -T neo4j cypher-shell -u neo4j -p "$NEO4J_PASSWORD" "RETURN 1" &> /dev/null; do
        attempt=$((attempt + 1))
        if [[ $attempt -ge $max_attempts ]]; then
            error "Neo4j failed to start after ${max_attempts} attempts"
            exit 1
        fi
        sleep 2
    done
    
    success "✅ Databases initialized successfully"
}

# Start all services
start_services() {
    info "🚀 Starting all platform services..."
    
    cd "$PROJECT_DIR"
    
    # Start all services
    docker-compose up -d
    
    # Wait for services to be ready
    info "⏳ Waiting for services to be ready..."
    sleep 45
    
    success "✅ All services started successfully"
}

# Verify deployment
verify_deployment() {
    info "🔍 Verifying deployment..."
    
    local services=(
        "unified-api:11070:/health"
        "discovery-engine:11050:/health"
        "valuation-engine:11060:/health"
        "unified-dashboard:11071:/"
        "grafana:11072:/"
    )
    
    local failed_services=()
    
    for service_config in "${services[@]}"; do
        IFS=':' read -r service port endpoint <<< "$service_config"
        
        info "Checking $service on port $port..."
        
        local max_attempts=10
        local attempt=0
        local success=false
        
        while [[ $attempt -lt $max_attempts ]]; do
            if curl -f -s "http://localhost:${port}${endpoint}" > /dev/null 2>&1; then
                success=true
                break
            fi
            attempt=$((attempt + 1))
            sleep 3
        done
        
        if [[ "$success" == true ]]; then
            success "✅ $service is responding"
        else
            error "❌ $service is not responding on port $port"
            failed_services+=("$service")
        fi
    done
    
    if [[ ${#failed_services[@]} -eq 0 ]]; then
        success "🎉 All services are healthy!"
    else
        warning "⚠️  Some services are not responding: ${failed_services[*]}"
        info "Check logs with: docker-compose logs [service-name]"
    fi
}

# Show access information
show_access_info() {
    echo -e "${CYAN}"
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║                    🎯 ACCESS INFORMATION                        ║"
    echo "╠════════════════════════════════════════════════════════════════╣"
    echo "║                                                                ║"
    echo "║  📊 Main Dashboard:     http://localhost:11071                ║"
    echo "║  🔌 Unified API:        http://localhost:11070                ║"
    echo "║  🔍 Discovery Engine:   http://localhost:11050                ║"
    echo "║  💰 Valuation Engine:   http://localhost:11060                ║"
    echo "║  📈 Monitoring:         http://localhost:11072                ║"
    echo "║                                                                ║"
    echo "║  📚 API Documentation:  http://localhost:11070/api/docs       ║"
    echo "║  🔍 Discovery Docs:     http://localhost:11050/docs           ║"
    echo "║  💰 Valuation Docs:     http://localhost:11060/docs           ║"
    echo "║                                                                ║"
    echo "║  🗄️  Database Access:                                          ║"
    echo "║     PostgreSQL:         localhost:5432                        ║"
    echo "║     Neo4j Browser:      http://localhost:7474                 ║"
    echo "║     Redis:              localhost:6379                        ║"
    echo "║                                                                ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Show management commands
show_management_commands() {
    echo -e "${YELLOW}"
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║                   🛠️  MANAGEMENT COMMANDS                       ║"
    echo "╠════════════════════════════════════════════════════════════════╣"
    echo "║                                                                ║"
    echo "║  View logs:          docker-compose logs -f [service]         ║"
    echo "║  Stop platform:      docker-compose down                      ║"
    echo "║  Restart service:    docker-compose restart [service]         ║"
    echo "║  Update images:      docker-compose pull && docker-compose up ║"
    echo "║                                                                ║"
    echo "║  Service names:                                                ║"
    echo "║    - unified-api                                               ║"
    echo "║    - discovery-engine                                          ║"
    echo "║    - valuation-engine                                          ║"
    echo "║    - unified-dashboard                                         ║"
    echo "║    - postgres, redis, neo4j                                    ║"
    echo "║    - prometheus, grafana                                       ║"
    echo "║                                                                ║"
    echo "║  Health check:       curl http://localhost:11070/health       ║"
    echo "║  System metrics:     curl http://localhost:11070/api/metrics  ║"
    echo "║                                                                ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Main execution
main() {
    show_banner
    
    info "🚀 Starting 4-Plex Unified Investment Platform deployment..."
    info "📝 Log file: $LOG_FILE"
    
    # Create log directory
    mkdir -p "$(dirname "$LOG_FILE")"
    
    # Execute deployment steps
    check_prerequisites
    setup_environment
    prepare_images
    initialize_databases
    start_services
    verify_deployment
    
    success "🎉 4-Plex Unified Investment Platform deployed successfully!"
    
    show_access_info
    show_management_commands
    
    info "📊 Platform is ready for use!"
    info "🔧 For troubleshooting, check: docker-compose logs -f"
}

# Handle script arguments
case "${1:-start}" in
    "start")
        main
        ;;
    "stop")
        info "🛑 Stopping 4-Plex Unified Platform..."
        cd "$PROJECT_DIR"
        docker-compose down
        success "✅ Platform stopped"
        ;;
    "restart")
        info "🔄 Restarting 4-Plex Unified Platform..."
        cd "$PROJECT_DIR"
        docker-compose restart
        verify_deployment
        success "✅ Platform restarted"
        ;;
    "status")
        info "📊 Checking platform status..."
        cd "$PROJECT_DIR"
        docker-compose ps
        verify_deployment
        ;;
    "logs")
        cd "$PROJECT_DIR"
        if [[ -n "${2}" ]]; then
            docker-compose logs -f "${2}"
        else
            docker-compose logs -f
        fi
        ;;
    "update")
        info "🔄 Updating platform..."
        cd "$PROJECT_DIR"
        docker-compose pull
        docker-compose up -d --build
        verify_deployment
        success "✅ Platform updated"
        ;;
    "clean")
        warning "🧹 This will remove all containers, volumes, and data!"
        echo -e "${YELLOW}Are you sure? (y/N)${NC}"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            cd "$PROJECT_DIR"
            docker-compose down -v --remove-orphans
            docker system prune -f
            success "✅ Platform cleaned"
        else
            info "❌ Cleanup cancelled"
        fi
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs [service]|update|clean}"
        echo ""
        echo "Commands:"
        echo "  start    - Start the unified platform (default)"
        echo "  stop     - Stop all services"
        echo "  restart  - Restart all services"
        echo "  status   - Show service status"
        echo "  logs     - Show logs (optionally for specific service)"
        echo "  update   - Update and rebuild services"
        echo "  clean    - Remove all containers and data (DESTRUCTIVE)"
        exit 1
        ;;
esac