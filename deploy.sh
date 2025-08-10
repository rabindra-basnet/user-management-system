#!/bin/bash

# User Management System Deployment Script
# This script helps deploy the system to various cloud platforms

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

# Function to deploy to Vercel (Frontend)
deploy_vercel() {
    print_status "Deploying frontend to Vercel..."
    
    if ! command_exists vercel; then
        print_error "Vercel CLI not found. Installing..."
        npm install -g vercel
    fi
    
    cd frontend
    
    # Create vercel.json if it doesn't exist
    if [ ! -f "vercel.json" ]; then
        cat > vercel.json << EOF
{
  "framework": "nextjs",
  "buildCommand": "npm run build",
  "devCommand": "npm run dev",
  "installCommand": "npm install",
  "env": {
    "NEXT_PUBLIC_API_URL": "@api_url"
  }
}
EOF
    fi
    
    print_status "Running Vercel deployment..."
    vercel --prod
    
    cd ..
    print_success "Frontend deployed to Vercel!"
}

# Function to deploy to Railway (Backend)
deploy_railway() {
    print_status "Deploying backend to Railway..."
    
    if ! command_exists railway; then
        print_error "Railway CLI not found. Please install it first:"
        echo "npm install -g @railway/cli"
        exit 1
    fi
    
    cd backend
    
    # Create railway.json if it doesn't exist
    if [ ! -f "railway.json" ]; then
        cat > railway.json << EOF
{
  "build": {
    "builder": "DOCKERFILE"
  },
  "deploy": {
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port \$PORT",
    "healthcheckPath": "/health"
  }
}
EOF
    fi
    
    print_status "Running Railway deployment..."
    railway login
    railway deploy
    
    cd ..
    print_success "Backend deployed to Railway!"
}

# Function to deploy to Heroku
deploy_heroku() {
    print_status "Deploying to Heroku..."
    
    if ! command_exists heroku; then
        print_error "Heroku CLI not found. Please install it first."
        exit 1
    fi
    
    # Create Procfile for backend
    if [ ! -f "backend/Procfile" ]; then
        echo "web: uvicorn app.main:app --host 0.0.0.0 --port \$PORT" > backend/Procfile
    fi
    
    # Create app.json for easy deployment
    if [ ! -f "app.json" ]; then
        cat > app.json << EOF
{
  "name": "User Management System",
  "description": "Enterprise-grade user management system with FastAPI and Next.js",
  "repository": "https://github.com/rabindra-basnet/user-management-system",
  "keywords": ["fastapi", "nextjs", "user-management", "authentication"],
  "env": {
    "SECRET_KEY": {
      "description": "Secret key for JWT tokens",
      "generator": "secret"
    },
    "DATABASE_URL": {
      "description": "PostgreSQL database URL"
    },
    "REDIS_URL": {
      "description": "Redis URL for caching"
    }
  },
  "addons": [
    "heroku-postgresql:hobby-dev",
    "heroku-redis:hobby-dev"
  ],
  "buildpacks": [
    {
      "url": "heroku/python"
    }
  ]
}
EOF
    fi
    
    print_status "Creating Heroku app..."
    heroku create user-management-system-$(date +%s)
    
    print_status "Adding buildpacks..."
    heroku buildpacks:add heroku/python
    
    print_status "Adding add-ons..."
    heroku addons:create heroku-postgresql:hobby-dev
    heroku addons:create heroku-redis:hobby-dev
    
    print_status "Setting environment variables..."
    heroku config:set SECRET_KEY=$(openssl rand -base64 32)
    heroku config:set DEBUG=false
    heroku config:set ENVIRONMENT=production
    
    print_status "Deploying to Heroku..."
    git subtree push --prefix=backend heroku main
    
    print_status "Running database migrations..."
    heroku run alembic upgrade head
    heroku run python -m app.db.init_db
    
    print_success "Deployed to Heroku!"
    heroku open
}

# Function to deploy to DigitalOcean App Platform
deploy_digitalocean() {
    print_status "Preparing DigitalOcean App Platform deployment..."
    
    # Create .do/app.yaml
    mkdir -p .do
    cat > .do/app.yaml << EOF
name: user-management-system
services:
- name: backend
  source_dir: /backend
  github:
    repo: rabindra-basnet/user-management-system
    branch: main
  run_command: uvicorn app.main:app --host 0.0.0.0 --port 8080
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: DATABASE_URL
    value: \${db.DATABASE_URL}
  - key: REDIS_URL
    value: \${redis.DATABASE_URL}
  - key: SECRET_KEY
    value: your-secret-key-change-this
  - key: DEBUG
    value: "false"
  http_port: 8080
  health_check:
    http_path: /health

- name: frontend
  source_dir: /frontend
  github:
    repo: rabindra-basnet/user-management-system
    branch: main
  run_command: npm start
  environment_slug: node-js
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: NEXT_PUBLIC_API_URL
    value: \${backend.PUBLIC_URL}
  http_port: 3000

databases:
- name: db
  engine: PG
  version: "13"
  size: db-s-dev-database

- name: redis
  engine: REDIS
  version: "6"
  size: db-s-dev-database
EOF
    
    print_success "DigitalOcean App Platform configuration created!"
    print_status "To deploy:"
    echo "1. Go to https://cloud.digitalocean.com/apps"
    echo "2. Click 'Create App'"
    echo "3. Connect your GitHub repository"
    echo "4. Use the configuration in .do/app.yaml"
}

# Function to deploy with Docker Compose
deploy_docker() {
    print_status "Deploying with Docker Compose..."
    
    # Create production docker-compose file
    cat > docker-compose.prod.yml << EOF
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/user_management
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=\${SECRET_KEY}
      - DEBUG=false
      - ENVIRONMENT=production
    depends_on:
      - db
      - redis
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    depends_on:
      - backend
    restart: unless-stopped

  db:
    image: postgres:13
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=user_management
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:6-alpine
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - frontend
      - backend
    restart: unless-stopped

volumes:
  postgres_data:
EOF
    
    # Create nginx configuration
    cat > nginx.conf << EOF
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }
    
    upstream frontend {
        server frontend:3000;
    }
    
    server {
        listen 80;
        server_name localhost;
        
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }
        
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }
    }
}
EOF
    
    print_status "Building and starting production containers..."
    docker-compose -f docker-compose.prod.yml up -d --build
    
    print_success "Production deployment with Docker Compose completed!"
}

# Function to display usage
show_usage() {
    echo "Usage: $0 [PLATFORM]"
    echo ""
    echo "Platforms:"
    echo "  vercel       Deploy frontend to Vercel"
    echo "  railway      Deploy backend to Railway"
    echo "  heroku       Deploy full stack to Heroku"
    echo "  digitalocean Create DigitalOcean App Platform config"
    echo "  docker       Deploy with Docker Compose (production)"
    echo "  help         Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 vercel     # Deploy frontend to Vercel"
    echo "  $0 heroku     # Deploy full stack to Heroku"
    echo "  $0 docker     # Deploy with Docker Compose"
}

# Main function
main() {
    echo "========================================="
    echo "  User Management System Deployment"
    echo "========================================="
    echo ""
    
    # Parse command line arguments
    case "${1:-}" in
        vercel)
            deploy_vercel
            ;;
        railway)
            deploy_railway
            ;;
        heroku)
            deploy_heroku
            ;;
        digitalocean)
            deploy_digitalocean
            ;;
        docker)
            deploy_docker
            ;;
        help)
            show_usage
            exit 0
            ;;
        "")
            print_error "No platform specified."
            show_usage
            exit 1
            ;;
        *)
            print_error "Unknown platform: $1"
            show_usage
            exit 1
            ;;
    esac
    
    echo ""
    echo "========================================="
    echo "  Deployment Complete!"
    echo "========================================="
    echo ""
    print_success "Your User Management System has been deployed!"
    echo ""
    echo "Next steps:"
    echo "1. Update environment variables in your platform"
    echo "2. Set up custom domain (optional)"
    echo "3. Configure SSL certificates"
    echo "4. Set up monitoring and logging"
    echo "5. Update README with live demo links"
}

# Run main function
main "$@"
