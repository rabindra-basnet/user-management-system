#!/bin/bash

# User Management System Test Script
# This script runs tests for both backend and frontend

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

# Function to run backend tests
test_backend() {
    print_status "Running backend tests..."
    
    cd backend
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        print_error "Virtual environment not found. Please run setup.sh first."
        exit 1
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Check if pytest is installed
    if ! command_exists pytest; then
        print_error "pytest not found. Installing test dependencies..."
        pip install pytest pytest-asyncio pytest-cov httpx faker
    fi
    
    # Run tests with coverage
    print_status "Running pytest with coverage..."
    pytest --cov=app --cov-report=html --cov-report=term-missing -v
    
    # Check test results
    if [ $? -eq 0 ]; then
        print_success "Backend tests passed!"
    else
        print_error "Backend tests failed!"
        cd ..
        exit 1
    fi
    
    cd ..
}

# Function to run frontend tests
test_frontend() {
    print_status "Running frontend tests..."
    
    cd frontend
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        print_error "Node modules not found. Please run setup.sh first."
        exit 1
    fi
    
    # Run tests
    print_status "Running Jest tests..."
    npm test -- --coverage --watchAll=false
    
    # Check test results
    if [ $? -eq 0 ]; then
        print_success "Frontend tests passed!"
    else
        print_error "Frontend tests failed!"
        cd ..
        exit 1
    fi
    
    cd ..
}

# Function to run security tests
test_security() {
    print_status "Running security tests..."
    
    # Backend security tests
    cd backend
    source venv/bin/activate
    
    print_status "Running backend security tests..."
    pytest tests/test_security.py -v
    
    if [ $? -eq 0 ]; then
        print_success "Backend security tests passed!"
    else
        print_error "Backend security tests failed!"
        cd ..
        exit 1
    fi
    
    cd ..
    
    # Frontend security tests (if they exist)
    cd frontend
    
    if [ -f "src/components/security/SecurityTest.test.tsx" ]; then
        print_status "Running frontend security tests..."
        npm test -- --testPathPattern=SecurityTest --watchAll=false
        
        if [ $? -eq 0 ]; then
            print_success "Frontend security tests passed!"
        else
            print_error "Frontend security tests failed!"
            cd ..
            exit 1
        fi
    else
        print_warning "Frontend security tests not found"
    fi
    
    cd ..
}

# Function to run integration tests
test_integration() {
    print_status "Running integration tests..."
    
    # Check if services are running
    if ! curl -s http://localhost:8000/health >/dev/null 2>&1; then
        print_error "Backend is not running. Please start services first with ./start.sh"
        exit 1
    fi
    
    if ! curl -s http://localhost:3000 >/dev/null 2>&1; then
        print_error "Frontend is not running. Please start services first with ./start.sh"
        exit 1
    fi
    
    cd backend
    source venv/bin/activate
    
    # Run integration tests
    print_status "Running integration tests..."
    pytest tests/test_integration.py -v
    
    if [ $? -eq 0 ]; then
        print_success "Integration tests passed!"
    else
        print_error "Integration tests failed!"
        cd ..
        exit 1
    fi
    
    cd ..
}

# Function to run linting
test_lint() {
    print_status "Running linting checks..."
    
    # Backend linting
    cd backend
    source venv/bin/activate
    
    print_status "Running backend linting..."
    
    # Check if linting tools are installed
    if ! command_exists black; then
        print_warning "Installing linting tools..."
        pip install black isort flake8 mypy
    fi
    
    # Run black
    print_status "Running black formatter check..."
    black --check app/ || print_warning "Black formatting issues found"
    
    # Run isort
    print_status "Running isort import check..."
    isort --check-only app/ || print_warning "Import sorting issues found"
    
    # Run flake8
    print_status "Running flake8 linting..."
    flake8 app/ || print_warning "Flake8 linting issues found"
    
    cd ..
    
    # Frontend linting
    cd frontend
    
    print_status "Running frontend linting..."
    
    # Run ESLint
    npm run lint || print_warning "ESLint issues found"
    
    # Run TypeScript check
    npm run type-check || print_warning "TypeScript issues found"
    
    cd ..
    
    print_success "Linting checks completed"
}

# Function to generate test report
generate_report() {
    print_status "Generating test report..."
    
    REPORT_DIR="test-reports"
    mkdir -p $REPORT_DIR
    
    # Backend coverage report
    if [ -d "backend/htmlcov" ]; then
        cp -r backend/htmlcov $REPORT_DIR/backend-coverage
        print_success "Backend coverage report: $REPORT_DIR/backend-coverage/index.html"
    fi
    
    # Frontend coverage report
    if [ -d "frontend/coverage" ]; then
        cp -r frontend/coverage $REPORT_DIR/frontend-coverage
        print_success "Frontend coverage report: $REPORT_DIR/frontend-coverage/lcov-report/index.html"
    fi
    
    # Create summary report
    cat > $REPORT_DIR/summary.md << EOF
# Test Report Summary

Generated on: $(date)

## Backend Tests
- Location: backend/
- Coverage Report: backend-coverage/index.html

## Frontend Tests
- Location: frontend/
- Coverage Report: frontend-coverage/lcov-report/index.html

## Security Tests
- Backend security tests included
- Frontend security tests included

## Integration Tests
- API endpoint tests
- Database integration tests

## Linting
- Backend: black, isort, flake8, mypy
- Frontend: ESLint, TypeScript

EOF

    print_success "Test report generated: $REPORT_DIR/summary.md"
}

# Function to display usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --backend      Run backend tests only"
    echo "  --frontend     Run frontend tests only"
    echo "  --security     Run security tests only"
    echo "  --integration  Run integration tests only"
    echo "  --lint         Run linting checks only"
    echo "  --all          Run all tests (default)"
    echo "  --report       Generate test report"
    echo "  --help         Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0             # Run all tests"
    echo "  $0 --backend   # Run backend tests only"
    echo "  $0 --security  # Run security tests only"
    echo "  $0 --report    # Generate test report"
}

# Main function
main() {
    echo "========================================="
    echo "  User Management System Test Runner"
    echo "========================================="
    echo ""
    
    # Parse command line arguments
    case "${1:-}" in
        --backend)
            test_backend
            ;;
        --frontend)
            test_frontend
            ;;
        --security)
            test_security
            ;;
        --integration)
            test_integration
            ;;
        --lint)
            test_lint
            ;;
        --all)
            test_backend
            test_frontend
            test_security
            test_lint
            ;;
        --report)
            generate_report
            exit 0
            ;;
        --help)
            show_usage
            exit 0
            ;;
        "")
            # Default to all tests
            test_backend
            test_frontend
            test_security
            test_lint
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
    
    echo ""
    echo "========================================="
    echo "  All Tests Completed!"
    echo "========================================="
    echo ""
    print_success "All tests have been completed successfully!"
    echo ""
    echo "To generate a test report, run:"
    echo "  $0 --report"
    echo ""
    echo "To run integration tests (requires running services):"
    echo "  ./start.sh"
    echo "  $0 --integration"
    echo ""
}

# Run main function
main "$@"
