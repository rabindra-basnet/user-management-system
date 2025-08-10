#!/bin/bash

# User Management System Stop Script
# This script stops the backend and frontend services

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

# Function to stop processes on port
stop_port() {
    local port=$1
    local service_name=$2
    
    print_status "Stopping $service_name on port $port..."
    
    # Find processes using the port
    local pids=$(lsof -ti :$port 2>/dev/null || true)
    
    if [ -z "$pids" ]; then
        print_warning "No processes found running on port $port"
        return
    fi
    
    # Kill the processes
    for pid in $pids; do
        print_status "Killing process $pid..."
        kill -TERM $pid 2>/dev/null || true
        
        # Wait a moment for graceful shutdown
        sleep 2
        
        # Force kill if still running
        if kill -0 $pid 2>/dev/null; then
            print_warning "Process $pid still running, force killing..."
            kill -KILL $pid 2>/dev/null || true
        fi
    done
    
    print_success "$service_name stopped successfully"
}

# Function to stop Docker services
stop_docker() {
    print_status "Stopping Docker services..."
    
    if ! command_exists docker; then
        print_error "Docker is not installed"
        return 1
    fi
    
    if ! command_exists docker-compose; then
        print_error "Docker Compose is not installed"
        return 1
    fi
    
    # Stop and remove containers
    docker-compose down
    
    print_success "Docker services stopped successfully"
}

# Function to stop manual services
stop_manual() {
    print_status "Stopping manual services..."
    
    # Stop backend (port 8000)
    stop_port 8000 "Backend"
    
    # Stop frontend (port 3000)
    stop_port 3000 "Frontend"
    
    # Stop any uvicorn processes
    print_status "Stopping uvicorn processes..."
    pkill -f "uvicorn.*app.main:app" 2>/dev/null || print_warning "No uvicorn processes found"
    
    # Stop any npm/node processes related to our project
    print_status "Stopping Node.js development server..."
    pkill -f "next.*dev" 2>/dev/null || print_warning "No Next.js dev processes found"
    
    print_success "Manual services stopped successfully"
}

# Function to stop all services
stop_all() {
    print_status "Stopping all services..."
    
    # Try to stop Docker services first
    if [ -f "docker-compose.yml" ]; then
        stop_docker 2>/dev/null || true
    fi
    
    # Stop manual services
    stop_manual
    
    print_success "All services stopped successfully"
}

# Function to check service status
check_status() {
    print_status "Checking service status..."
    
    # Check backend
    if lsof -i :8000 >/dev/null 2>&1; then
        print_warning "Backend is still running on port 8000"
    else
        print_success "Backend is not running"
    fi
    
    # Check frontend
    if lsof -i :3000 >/dev/null 2>&1; then
        print_warning "Frontend is still running on port 3000"
    else
        print_success "Frontend is not running"
    fi
    
    # Check Docker services
    if command_exists docker-compose && [ -f "docker-compose.yml" ]; then
        if docker-compose ps | grep -q "Up"; then
            print_warning "Docker services are still running"
        else
            print_success "Docker services are not running"
        fi
    fi
}

# Function to display usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --docker     Stop Docker services only"
    echo "  --manual     Stop manual services only"
    echo "  --all        Stop all services (default)"
    echo "  --check      Check service status"
    echo "  --help       Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0           # Stop all services"
    echo "  $0 --docker  # Stop Docker services only"
    echo "  $0 --manual  # Stop manual services only"
    echo "  $0 --check   # Check service status"
}

# Main function
main() {
    echo "========================================="
    echo "  User Management System Stopper"
    echo "========================================="
    echo ""
    
    # Parse command line arguments
    case "${1:-}" in
        --docker)
            stop_docker
            ;;
        --manual)
            stop_manual
            ;;
        --all)
            stop_all
            ;;
        --check)
            check_status
            exit 0
            ;;
        --help)
            show_usage
            exit 0
            ;;
        "")
            # Default to stop all
            stop_all
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
    
    echo ""
    echo "========================================="
    echo "  Stop Complete!"
    echo "========================================="
    echo ""
    
    # Check final status
    check_status
    
    echo ""
    print_success "User Management System services have been stopped!"
    echo ""
    echo "To start the services again, run:"
    echo "  ./start.sh"
    echo ""
}

# Run main function
main "$@"
