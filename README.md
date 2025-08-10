# User Management System

![Python](https://img.shields.io/badge/python-v3.9+-blue.svg)
![Node.js](https://img.shields.io/badge/node.js-v18+-green.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-red.svg)
![Next.js](https://img.shields.io/badge/Next.js-14+-black.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Build](https://github.com/rabindra-basnet/user-management-system/workflows/CI/CD%20Pipeline/badge.svg)
![Security](https://img.shields.io/badge/security-enterprise--grade-green.svg)

A comprehensive, production-ready user management system built with FastAPI (backend) and Next.js (frontend), featuring advanced security measures, role-based access control, and modern UI components.

## 🌟 Live Demo

- **Frontend**: [Demo Link](https://your-demo-url.vercel.app) *(Deploy to get live link)*
- **API Documentation**: [API Docs](https://your-api-url.herokuapp.com/docs) *(Deploy to get live link)*
- **Repository**: [GitHub](https://github.com/rabindra-basnet/user-management-system)

## 🚀 Features

### Security Features
- **JWT Authentication** with access and refresh tokens
- **Two-Factor Authentication (2FA)** with TOTP and backup codes
- **Role-Based Access Control (RBAC)** with granular permissions
- **Password Security** with strength validation and hashing
- **Rate Limiting** to prevent brute force attacks
- **Session Management** with device tracking
- **API Key Authentication** for programmatic access
- **Security Headers** and CORS protection
- **Audit Logging** for all user actions
- **Account Lockout** after failed login attempts

### User Management
- **User Registration** with email verification
- **User Profiles** with customizable fields
- **User Search** and filtering
- **Bulk Operations** for user management
- **User Statistics** and analytics
- **Account Activation/Deactivation**
- **Password Reset** functionality

### Admin Features
- **Admin Dashboard** with key metrics
- **User Management Interface**
- **Role and Permission Management**
- **Audit Log Viewer**
- **System Settings**
- **API Key Management**

### Technical Features
- **Modern Tech Stack** (FastAPI + Next.js + TypeScript)
- **Database Migrations** with Alembic
- **API Documentation** with OpenAPI/Swagger
- **Type Safety** throughout the application
- **Responsive Design** with Tailwind CSS
- **Real-time Updates** with React Query
- **Form Validation** with Zod and React Hook Form
- **State Management** with Zustand
- **Testing Ready** with Jest and pytest

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - SQL toolkit and ORM
- **PostgreSQL** - Primary database
- **Redis** - Caching and rate limiting
- **Alembic** - Database migrations
- **Pydantic** - Data validation
- **JWT** - Authentication tokens
- **Bcrypt** - Password hashing
- **TOTP** - Two-factor authentication

### Frontend
- **Next.js 14** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Utility-first CSS
- **React Query** - Data fetching and caching
- **Zustand** - State management
- **React Hook Form** - Form handling
- **Zod** - Schema validation
- **Headless UI** - Accessible components
- **Heroicons** - Icon library

## 🚀 Quick Start with Scripts

We provide automated scripts for easy setup and management:

### Available Scripts

- **`setup.sh`** - Automated setup and installation
- **`start.sh`** - Start all services
- **`stop.sh`** - Stop all services
- **`test.sh`** - Run tests and checks
- **`health-check.sh`** - Check system health

### Quick Setup

```bash
# Clone the repository
git clone <repository-url>
cd user-management-system

# Make scripts executable (Linux/Mac)
chmod +x *.sh

# Run automated setup
./setup.sh

# Start the services
./start.sh

# Check system health
./health-check.sh
```

### Script Usage

#### Setup Script
```bash
./setup.sh --docker    # Setup with Docker (recommended)
./setup.sh --manual    # Manual setup
./setup.sh --help      # Show help
```

#### Start Script
```bash
./start.sh             # Start manually
./start.sh --docker    # Start with Docker
./start.sh --check     # Check service status
```

#### Stop Script
```bash
./stop.sh              # Stop all services
./stop.sh --docker     # Stop Docker services only
./stop.sh --manual     # Stop manual services only
```

#### Test Script
```bash
./test.sh              # Run all tests
./test.sh --backend    # Backend tests only
./test.sh --frontend   # Frontend tests only
./test.sh --security   # Security tests only
```

#### Health Check Script
```bash
./health-check.sh      # Check all components
./health-check.sh --services  # Check running services
./health-check.sh --database  # Check database only
```

## 📦 Manual Installation

### Prerequisites
- Python 3.9+
- Node.js 18+
- PostgreSQL 12+
- Redis 6+

### Backend Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd user-management-system/backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Environment configuration**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Database setup**
```bash
# Create database
createdb user_management

# Run migrations
alembic upgrade head

# Create initial admin user
python -m app.initial_data
```

6. **Start the server**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

1. **Navigate to frontend directory**
```bash
cd ../frontend
```

2. **Install dependencies**
```bash
npm install
```

3. **Environment configuration**
```bash
cp .env.example .env.local
# Edit .env.local with your configuration
```

4. **Start development server**
```bash
npm run dev
```

## 🔧 Configuration

### Backend Configuration (.env)
```env
# Application
APP_NAME=User Management System
DEBUG=true

# Database
DATABASE_URL=postgresql://user:password@localhost/user_management

# Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Redis
REDIS_URL=redis://localhost:6379

# Email (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Admin User
FIRST_SUPERUSER_EMAIL=admin@example.com
FIRST_SUPERUSER_PASSWORD=admin123
```

### Frontend Configuration (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🚦 Usage

### Default Admin Account
- **Email**: admin@example.com
- **Password**: admin123

**⚠️ Important**: Change the default admin credentials immediately after first login.

### API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Frontend Application
- **Development**: http://localhost:3000
- **Login Page**: http://localhost:3000/login
- **Dashboard**: http://localhost:3000/dashboard

## 🔐 Security Best Practices

### Password Requirements
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character

### Two-Factor Authentication
1. Enable 2FA in user settings
2. Scan QR code with authenticator app
3. Save backup codes securely
4. Verify with 6-digit code

### API Security
- All endpoints require authentication
- Rate limiting on sensitive endpoints
- CORS protection configured
- Security headers added automatically
- SQL injection protection via ORM

## 📊 Monitoring and Logging

### Audit Logs
All user actions are logged including:
- Login/logout events
- User creation/modification
- Role assignments
- Permission changes
- Failed authentication attempts

### Security Monitoring
- Failed login attempt tracking
- Account lockout mechanisms
- Session monitoring
- API usage tracking

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

### Coverage Reports
```bash
# Backend
pytest --cov=app

# Frontend
npm run test:coverage
```

## 🚀 Deployment

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up -d
```

### Production Considerations
- Use environment variables for secrets
- Enable HTTPS/SSL
- Configure proper CORS origins
- Set up database backups
- Monitor application logs
- Use a reverse proxy (nginx)
- Enable rate limiting
- Set up health checks

## 📝 API Reference

### Authentication Endpoints
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/logout` - User logout
- `GET /api/v1/auth/me` - Get current user

### User Management Endpoints
- `GET /api/v1/users/` - List users
- `POST /api/v1/users/` - Create user
- `GET /api/v1/users/{id}` - Get user
- `PUT /api/v1/users/{id}` - Update user
- `DELETE /api/v1/users/{id}` - Delete user

### Role Management Endpoints
- `GET /api/v1/roles/` - List roles
- `POST /api/v1/roles/` - Create role
- `PUT /api/v1/roles/{id}` - Update role
- `DELETE /api/v1/roles/{id}` - Delete role

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the API documentation at `/docs`

## 🔄 Changelog

### v1.0.0
- Initial release
- Complete user management system
- Role-based access control
- Two-factor authentication
- Modern UI with Next.js
- Comprehensive security features
