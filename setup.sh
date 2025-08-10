#!/bin/bash

# User Management System Setup Script
# This script sets up the entire user management system

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

# Function to check system requirements
check_requirements() {
    print_status "Checking system requirements..."
    
    # Check Python
    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_success "Python $PYTHON_VERSION found"
    else
        print_error "Python 3.9+ is required but not found"
        exit 1
    fi
    
    # Check Node.js
    if command_exists node; then
        NODE_VERSION=$(node --version)
        print_success "Node.js $NODE_VERSION found"
    else
        print_error "Node.js 18+ is required but not found"
        exit 1
    fi
    
    # Check npm
    if command_exists npm; then
        NPM_VERSION=$(npm --version)
        print_success "npm $NPM_VERSION found"
    else
        print_error "npm is required but not found"
        exit 1
    fi
    
    # Check PostgreSQL
    if command_exists psql; then
        POSTGRES_VERSION=$(psql --version | cut -d' ' -f3)
        print_success "PostgreSQL $POSTGRES_VERSION found"
    else
        print_warning "PostgreSQL not found. You'll need to install it or use Docker"
    fi
    
    # Check Redis
    if command_exists redis-cli; then
        print_success "Redis CLI found"
    else
        print_warning "Redis not found. You'll need to install it or use Docker"
    fi
    
    # Check Docker (optional)
    if command_exists docker; then
        DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | sed 's/,//')
        print_success "Docker $DOCKER_VERSION found"
    else
        print_warning "Docker not found. Manual setup will be required"
    fi
}

# Function to setup backend
setup_backend() {
    print_status "Setting up backend..."
    
    cd backend
    
    # Create virtual environment
    print_status "Creating Python virtual environment..."
    python3 -m venv venv
    
    # Activate virtual environment
    print_status "Activating virtual environment..."
    source venv/bin/activate
    
    # Upgrade pip
    print_status "Upgrading pip..."
    pip install --upgrade pip
    
    # Install dependencies
    print_status "Installing Python dependencies..."
    pip install -r requirements.txt
    
    # Copy environment file
    if [ ! -f .env ]; then
        print_status "Creating environment file..."
        cp .env.example .env
        print_warning "Please edit backend/.env with your database and Redis URLs"
    fi
    
    cd ..
    print_success "Backend setup completed"
}

# Function to setup frontend
setup_frontend() {
    print_status "Setting up frontend..."
    
    cd frontend
    
    # Install dependencies
    print_status "Installing Node.js dependencies..."
    npm install
    
    # Copy environment file
    if [ ! -f .env.local ]; then
        print_status "Creating environment file..."
        cp .env.example .env.local
        print_warning "Please edit frontend/.env.local with your API URL"
    fi
    
    cd ..
    print_success "Frontend setup completed"
}

# Function to setup database
setup_database() {
    print_status "Setting up database..."
    
    # Check if PostgreSQL is running
    if ! command_exists psql; then
        print_warning "PostgreSQL not found. Skipping database setup."
        print_warning "Please ensure PostgreSQL is running and create a database named 'user_management'"
        return
    fi
    
    # Try to create database
    print_status "Creating database..."
    createdb user_management 2>/dev/null || print_warning "Database may already exist"
    
    # Run migrations
    print_status "Running database migrations..."
    cd backend
    source venv/bin/activate
    alembic upgrade head
    
    # Initialize default data
    print_status "Initializing default data..."
    python -m app.db.init_db
    
    cd ..
    print_success "Database setup completed"
}

# Function to setup with Docker
setup_docker() {
    print_status "Setting up with Docker..."
    
    if ! command_exists docker; then
        print_error "Docker is required for this setup method"
        exit 1
    fi
    
    if ! command_exists docker-compose; then
        print_error "Docker Compose is required for this setup method"
        exit 1
    fi
    
    # Copy environment files
    if [ ! -f backend/.env ]; then
        cp backend/.env.example backend/.env
    fi
    
    if [ ! -f frontend/.env.local ]; then
        cp frontend/.env.example frontend/.env.local
    fi
    
    # Build and start services
    print_status "Building and starting Docker services..."
    docker-compose up -d --build
    
    # Wait for services to be ready
    print_status "Waiting for services to be ready..."
    sleep 30
    
    # Run database migrations
    print_status "Running database migrations..."
    docker-compose exec backend alembic upgrade head
    
    # Initialize default data
    print_status "Initializing default data..."
    docker-compose exec backend python -m app.db.init_db
    
    print_success "Docker setup completed"
}

# Function to display usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --docker     Setup using Docker (recommended)"
    echo "  --manual     Setup manually (requires PostgreSQL and Redis)"
    echo "  --help       Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --docker    # Setup with Docker"
    echo "  $0 --manual    # Manual setup"
}

# Main setup function
main() {
    echo "========================================="
    echo "  User Management System Setup"
    echo "========================================="
    echo ""
    
    # Parse command line arguments
    case "${1:-}" in
        --docker)
            check_requirements
            setup_docker
            ;;
        --manual)
            check_requirements
            setup_backend
            setup_frontend
            setup_database
            ;;
        --help)
            show_usage
            exit 0
            ;;
        "")
            print_status "No setup method specified. Checking for Docker..."
            if command_exists docker && command_exists docker-compose; then
                print_status "Docker found. Using Docker setup..."
                check_requirements
                setup_docker
            else
                print_status "Docker not found. Using manual setup..."
                check_requirements
                setup_backend
                setup_frontend
                setup_database
            fi
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
    
    echo ""
    echo "========================================="
    echo "  Setup Complete!"
    echo "========================================="
    echo ""
    print_success "User Management System has been set up successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Edit configuration files if needed:"
    echo "   - backend/.env (database and Redis URLs)"
    echo "   - frontend/.env.local (API URL)"
    echo ""
    echo "2. Start the services:"
    if [ "${1:-}" = "--docker" ]; then
        echo "   docker-compose up -d"
    else
        echo "   ./start.sh"
    fi
    echo ""
    echo "3. Access the application:"
    echo "   - Frontend: http://localhost:3000"
    echo "   - Backend API: http://localhost:8000"
    echo "   - API Docs: http://localhost:8000/docs"
    echo ""
    echo "4. Default admin credentials:"
    echo "   - Email: admin@example.com"
    echo "   - Password: admin123"
    echo ""
    print_warning "Remember to change the default admin password!"
}

# Run main function
main "$@"
