#!/bin/bash

# Fix Build Issues Script
# This script fixes common build issues with the User Management System

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

# Function to fix frontend dependencies
fix_frontend_deps() {
    print_status "Fixing frontend dependencies..."
    
    cd frontend
    
    # Remove node_modules and package-lock.json
    rm -rf node_modules package-lock.json
    
    # Install dependencies
    npm install
    
    # Install missing dependencies
    npm install react@18.2.0 react-dom@18.2.0
    npm install @types/react@18.2.37 @types/react-dom@18.2.15
    npm install react-hot-toast@2.4.1
    npm install @headlessui/react@1.7.17
    
    cd ..
    print_success "Frontend dependencies fixed"
}

# Function to fix backend dependencies
fix_backend_deps() {
    print_status "Fixing backend dependencies..."
    
    cd backend
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        print_status "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install dependencies
    pip install -r requirements.txt
    
    cd ..
    print_success "Backend dependencies fixed"
}

# Function to fix Docker build
fix_docker_build() {
    print_status "Fixing Docker build configuration..."
    
    # Stop any running containers
    docker-compose down 2>/dev/null || true
    
    # Remove old images
    docker rmi user-management-system-frontend 2>/dev/null || true
    docker rmi user-management-system-backend 2>/dev/null || true
    
    # Build with no cache
    print_status "Building Docker images..."
    docker-compose build --no-cache
    
    print_success "Docker build fixed"
}

# Function to test build
test_build() {
    print_status "Testing build..."
    
    # Test frontend build
    cd frontend
    print_status "Testing frontend build..."
    npm run build
    cd ..
    
    # Test backend
    cd backend
    if [ -d "venv" ]; then
        source venv/bin/activate
        print_status "Testing backend imports..."
        python -c "from app.main import app; print('Backend imports successful')"
    fi
    cd ..
    
    print_success "Build test completed"
}

# Function to display usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --frontend   Fix frontend dependencies only"
    echo "  --backend    Fix backend dependencies only"
    echo "  --docker     Fix Docker build only"
    echo "  --test       Test build only"
    echo "  --all        Fix all issues (default)"
    echo "  --help       Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0           # Fix all issues"
    echo "  $0 --frontend # Fix frontend only"
    echo "  $0 --docker   # Fix Docker build only"
}

# Main function
main() {
    echo "========================================="
    echo "  User Management System Build Fixer"
    echo "========================================="
    echo ""
    
    # Parse command line arguments
    case "${1:-}" in
        --frontend)
            fix_frontend_deps
            ;;
        --backend)
            fix_backend_deps
            ;;
        --docker)
            fix_docker_build
            ;;
        --test)
            test_build
            ;;
        --all)
            fix_frontend_deps
            fix_backend_deps
            fix_docker_build
            test_build
            ;;
        --help)
            show_usage
            exit 0
            ;;
        "")
            # Default to fix all
            fix_frontend_deps
            fix_backend_deps
            fix_docker_build
            test_build
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
    
    echo ""
    echo "========================================="
    echo "  Build Issues Fixed!"
    echo "========================================="
    echo ""
    print_success "All build issues have been resolved!"
    echo ""
    echo "You can now:"
    echo "1. Start the services: ./start.sh"
    echo "2. Run tests: ./test.sh"
    echo "3. Build with Docker: docker-compose up --build"
    echo ""
}

# Run main function
main "$@"
