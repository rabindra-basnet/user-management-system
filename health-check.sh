#!/bin/bash

# User Management System Health Check Script
# This script checks the health of all system components

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if port is in use
port_in_use() {
    if command_exists lsof; then
        lsof -i :$1 >/dev/null 2>&1
    elif command_exists netstat; then
        netstat -an | grep ":$1 " >/dev/null 2>&1
    else
        return 1
    fi
}

# Function to check HTTP endpoint
check_http() {
    local url=$1
    local name=$2
    local timeout=${3:-10}
    
    if command_exists curl; then
        if curl -s --max-time $timeout "$url" >/dev/null 2>&1; then
            print_success "$name is responding"
            return 0
        else
            print_error "$name is not responding"
            return 1
        fi
    else
        print_warning "curl not found, cannot check $name"
        return 1
    fi
}

# Function to check database connection
check_database() {
    print_status "Checking database connection..."
    
    if [ -f "backend/.env" ]; then
        source backend/.env
    else
        print_warning "Backend .env file not found"
        return 1
    fi
    
    if command_exists psql; then
        # Extract database info from DATABASE_URL
        if [ ! -z "$DATABASE_URL" ]; then
            if psql "$DATABASE_URL" -c "SELECT 1;" >/dev/null 2>&1; then
                print_success "Database connection successful"
                return 0
            else
                print_error "Database connection failed"
                return 1
            fi
        else
            print_warning "DATABASE_URL not set"
            return 1
        fi
    else
        print_warning "psql not found, cannot check database"
        return 1
    fi
}

# Function to check Redis connection
check_redis() {
    print_status "Checking Redis connection..."
    
    if [ -f "backend/.env" ]; then
        source backend/.env
    else
        print_warning "Backend .env file not found"
        return 1
    fi
    
    if command_exists redis-cli; then
        if [ ! -z "$REDIS_URL" ]; then
            # Extract Redis info from REDIS_URL
            local redis_host=$(echo $REDIS_URL | sed 's/redis:\/\///' | cut -d':' -f1)
            local redis_port=$(echo $REDIS_URL | sed 's/redis:\/\///' | cut -d':' -f2 | cut -d'/' -f1)
            
            if redis-cli -h ${redis_host:-localhost} -p ${redis_port:-6379} ping >/dev/null 2>&1; then
                print_success "Redis connection successful"
                return 0
            else
                print_error "Redis connection failed"
                return 1
            fi
        else
            print_warning "REDIS_URL not set"
            return 1
        fi
    else
        print_warning "redis-cli not found, cannot check Redis"
        return 1
    fi
}

# Function to check backend health
check_backend() {
    print_status "Checking backend service..."
    
    # Check if backend port is in use
    if port_in_use 8000; then
        print_success "Backend port 8000 is in use"
        
        # Check health endpoint
        if check_http "http://localhost:8000/health" "Backend health endpoint"; then
            # Check API endpoint
            if check_http "http://localhost:8000/api/v1/health" "Backend API endpoint"; then
                print_success "Backend service is healthy"
                return 0
            fi
        fi
    else
        print_error "Backend port 8000 is not in use"
        return 1
    fi
    
    return 1
}

# Function to check frontend health
check_frontend() {
    print_status "Checking frontend service..."
    
    # Check if frontend port is in use
    if port_in_use 3000; then
        print_success "Frontend port 3000 is in use"
        
        # Check frontend endpoint
        if check_http "http://localhost:3000" "Frontend"; then
            print_success "Frontend service is healthy"
            return 0
        fi
    else
        print_error "Frontend port 3000 is not in use"
        return 1
    fi
    
    return 1
}

# Function to check Docker services
check_docker_services() {
    print_status "Checking Docker services..."
    
    if ! command_exists docker; then
        print_warning "Docker not found"
        return 1
    fi
    
    if ! command_exists docker-compose; then
        print_warning "Docker Compose not found"
        return 1
    fi
    
    if [ ! -f "docker-compose.yml" ]; then
        print_warning "docker-compose.yml not found"
        return 1
    fi
    
    # Check if services are running
    local running_services=$(docker-compose ps --services --filter "status=running" 2>/dev/null | wc -l)
    local total_services=$(docker-compose ps --services 2>/dev/null | wc -l)
    
    if [ $running_services -eq $total_services ] && [ $total_services -gt 0 ]; then
        print_success "All Docker services are running ($running_services/$total_services)"
        return 0
    else
        print_error "Some Docker services are not running ($running_services/$total_services)"
        return 1
    fi
}

# Function to check system requirements
check_system_requirements() {
    print_status "Checking system requirements..."
    
    local all_good=true
    
    # Check Python
    if command_exists python3; then
        local python_version=$(python3 --version | cut -d' ' -f2)
        print_success "Python $python_version found"
    else
        print_error "Python 3.9+ is required but not found"
        all_good=false
    fi
    
    # Check Node.js
    if command_exists node; then
        local node_version=$(node --version)
        print_success "Node.js $node_version found"
    else
        print_error "Node.js 18+ is required but not found"
        all_good=false
    fi
    
    # Check npm
    if command_exists npm; then
        local npm_version=$(npm --version)
        print_success "npm $npm_version found"
    else
        print_error "npm is required but not found"
        all_good=false
    fi
    
    if $all_good; then
        print_success "All system requirements met"
        return 0
    else
        print_error "Some system requirements are missing"
        return 1
    fi
}

# Function to check project setup
check_project_setup() {
    print_status "Checking project setup..."
    
    local all_good=true
    
    # Check backend setup
    if [ -d "backend/venv" ]; then
        print_success "Backend virtual environment found"
    else
        print_error "Backend virtual environment not found"
        all_good=false
    fi
    
    if [ -f "backend/.env" ]; then
        print_success "Backend environment file found"
    else
        print_error "Backend environment file not found"
        all_good=false
    fi
    
    # Check frontend setup
    if [ -d "frontend/node_modules" ]; then
        print_success "Frontend node_modules found"
    else
        print_error "Frontend node_modules not found"
        all_good=false
    fi
    
    if [ -f "frontend/.env.local" ]; then
        print_success "Frontend environment file found"
    else
        print_error "Frontend environment file not found"
        all_good=false
    fi
    
    if $all_good; then
        print_success "Project setup is complete"
        return 0
    else
        print_error "Project setup is incomplete"
        return 1
    fi
}

# Function to display usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --all          Check all components (default)"
    echo "  --system       Check system requirements only"
    echo "  --setup        Check project setup only"
    echo "  --services     Check running services only"
    echo "  --docker       Check Docker services only"
    echo "  --database     Check database connection only"
    echo "  --redis        Check Redis connection only"
    echo "  --help         Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0             # Check all components"
    echo "  $0 --services  # Check running services only"
    echo "  $0 --database  # Check database connection only"
}

# Main function
main() {
    echo "========================================="
    echo "  User Management System Health Check"
    echo "========================================="
    echo ""
    
    local overall_health=true
    
    # Parse command line arguments
    case "${1:-}" in
        --system)
            check_system_requirements || overall_health=false
            ;;
        --setup)
            check_project_setup || overall_health=false
            ;;
        --services)
            check_backend || overall_health=false
            check_frontend || overall_health=false
            ;;
        --docker)
            check_docker_services || overall_health=false
            ;;
        --database)
            check_database || overall_health=false
            ;;
        --redis)
            check_redis || overall_health=false
            ;;
        --all)
            check_system_requirements || overall_health=false
            check_project_setup || overall_health=false
            check_database || overall_health=false
            check_redis || overall_health=false
            check_backend || overall_health=false
            check_frontend || overall_health=false
            check_docker_services || true  # Docker is optional
            ;;
        --help)
            show_usage
            exit 0
            ;;
        "")
            # Default to all checks
            check_system_requirements || overall_health=false
            check_project_setup || overall_health=false
            check_database || overall_health=false
            check_redis || overall_health=false
            check_backend || overall_health=false
            check_frontend || overall_health=false
            check_docker_services || true  # Docker is optional
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
    
    echo ""
    echo "========================================="
    echo "  Health Check Complete"
    echo "========================================="
    echo ""
    
    if $overall_health; then
        print_success "System is healthy!"
        echo ""
        echo "All components are working correctly."
        echo "You can access the application at:"
        echo "  - Frontend: http://localhost:3000"
        echo "  - Backend API: http://localhost:8000"
        echo "  - API Documentation: http://localhost:8000/docs"
        exit 0
    else
        print_error "System has health issues!"
        echo ""
        echo "Some components are not working correctly."
        echo "Please check the errors above and fix them."
        echo ""
        echo "Common solutions:"
        echo "  - Run ./setup.sh to set up the project"
        echo "  - Run ./start.sh to start the services"
        echo "  - Check the logs for more details"
        exit 1
    fi
}

# Run main function
main "$@"
