#!/bin/bash

# User Management System Start Script
# This script starts the backend and frontend services

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
    lsof -i :$1 >/dev/null 2>&1
}

# Function to start backend
start_backend() {
    print_status "Starting backend server..."
    
    cd backend
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        print_error "Virtual environment not found. Please run setup.sh first."
        exit 1
    fi
    
    # Check if .env file exists
    if [ ! -f ".env" ]; then
        print_error "Environment file not found. Please run setup.sh first."
        exit 1
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Check if port 8000 is in use
    if port_in_use 8000; then
        print_warning "Port 8000 is already in use. Backend may already be running."
    fi
    
    # Start the backend server
    print_status "Starting FastAPI server on http://localhost:8000"
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    
    cd ..
    
    # Wait a moment for the server to start
    sleep 3
    
    # Check if backend is running
    if curl -s http://localhost:8000/health >/dev/null 2>&1; then
        print_success "Backend server started successfully (PID: $BACKEND_PID)"
    else
        print_error "Failed to start backend server"
        exit 1
    fi
}

# Function to start frontend
start_frontend() {
    print_status "Starting frontend server..."
    
    cd frontend
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        print_error "Node modules not found. Please run setup.sh first."
        exit 1
    fi
    
    # Check if .env.local file exists
    if [ ! -f ".env.local" ]; then
        print_error "Environment file not found. Please run setup.sh first."
        exit 1
    fi
    
    # Check if port 3000 is in use
    if port_in_use 3000; then
        print_warning "Port 3000 is already in use. Frontend may already be running."
    fi
    
    # Start the frontend server
    print_status "Starting Next.js server on http://localhost:3000"
    npm run dev &
    FRONTEND_PID=$!
    
    cd ..
    
    # Wait a moment for the server to start
    sleep 5
    
    # Check if frontend is running
    if curl -s http://localhost:3000 >/dev/null 2>&1; then
        print_success "Frontend server started successfully (PID: $FRONTEND_PID)"
    else
        print_error "Failed to start frontend server"
        exit 1
    fi
}

# Function to start with Docker
start_docker() {
    print_status "Starting services with Docker..."
    
    if ! command_exists docker; then
        print_error "Docker is required for this start method"
        exit 1
    fi
    
    if ! command_exists docker-compose; then
        print_error "Docker Compose is required for this start method"
        exit 1
    fi
    
    # Start services
    docker-compose up -d
    
    # Wait for services to be ready
    print_status "Waiting for services to be ready..."
    sleep 10
    
    # Check if services are running
    if docker-compose ps | grep -q "Up"; then
        print_success "Docker services started successfully"
    else
        print_error "Failed to start Docker services"
        docker-compose logs
        exit 1
    fi
}

# Function to check services
check_services() {
    print_status "Checking service status..."
    
    # Check backend
    if curl -s http://localhost:8000/health >/dev/null 2>&1; then
        print_success "Backend is running on http://localhost:8000"
    else
        print_error "Backend is not responding on http://localhost:8000"
    fi
    
    # Check frontend
    if curl -s http://localhost:3000 >/dev/null 2>&1; then
        print_success "Frontend is running on http://localhost:3000"
    else
        print_error "Frontend is not responding on http://localhost:3000"
    fi
    
    # Check database (if not using Docker)
    if [ "${1:-}" != "--docker" ]; then
        cd backend
        if [ -f "venv/bin/activate" ]; then
            source venv/bin/activate
            if python -c "from app.db.session import engine; engine.connect()" 2>/dev/null; then
                print_success "Database connection is working"
            else
                print_error "Database connection failed"
            fi
        fi
        cd ..
    fi
}

# Function to display usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --docker     Start using Docker Compose"
    echo "  --manual     Start manually (default)"
    echo "  --check      Check service status"
    echo "  --help       Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0           # Start manually"
    echo "  $0 --docker  # Start with Docker"
    echo "  $0 --check   # Check service status"
}

# Function to handle cleanup on exit
cleanup() {
    if [ ! -z "${BACKEND_PID:-}" ]; then
        print_status "Stopping backend server (PID: $BACKEND_PID)..."
        kill $BACKEND_PID 2>/dev/null || true
    fi
    
    if [ ! -z "${FRONTEND_PID:-}" ]; then
        print_status "Stopping frontend server (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID 2>/dev/null || true
    fi
}

# Set up signal handlers
trap cleanup EXIT INT TERM

# Main function
main() {
    echo "========================================="
    echo "  User Management System Starter"
    echo "========================================="
    echo ""
    
    # Parse command line arguments
    case "${1:-}" in
        --docker)
            start_docker
            check_services --docker
            ;;
        --manual)
            start_backend
            start_frontend
            check_services
            ;;
        --check)
            check_services
            exit 0
            ;;
        --help)
            show_usage
            exit 0
            ;;
        "")
            # Default to manual start
            start_backend
            start_frontend
            check_services
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
    
    echo ""
    echo "========================================="
    echo "  Services Started Successfully!"
    echo "========================================="
    echo ""
    print_success "User Management System is now running!"
    echo ""
    echo "Access the application:"
    echo "  - Frontend: http://localhost:3000"
    echo "  - Backend API: http://localhost:8000"
    echo "  - API Documentation: http://localhost:8000/docs"
    echo ""
    echo "Default admin credentials:"
    echo "  - Email: admin@example.com"
    echo "  - Password: admin123"
    echo ""
    print_warning "Remember to change the default admin password!"
    echo ""
    
    if [ "${1:-}" != "--docker" ]; then
        echo "Press Ctrl+C to stop the services"
        echo ""
        
        # Keep the script running
        while true; do
            sleep 1
        done
    fi
}

# Run main function
main "$@"
