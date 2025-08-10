# 🔧 Build Fix Guide

This guide helps you resolve common build issues with the User Management System.

## 🚨 Common Build Issues & Solutions

### Issue 1: Missing Dependencies

**Error**: `Module not found: Can't resolve '@tanstack/react-query-devtools'`

**Solution**:
```bash
cd frontend
npm install @tanstack/react-query-devtools --save-dev
npm install @headlessui/react
npm install react-hot-toast
```

### Issue 2: Next.js Configuration Warning

**Error**: `Invalid next.config.js options detected: Unrecognized key(s) in object: 'appDir'`

**Solution**: The `appDir` option has been removed in Next.js 14. This is already fixed in the configuration.

### Issue 3: Docker Build Failures

**Error**: Build fails during `npm run build`

**Solution**:
```bash
# Use the fix script
chmod +x fix-build.sh
./fix-build.sh

# Or manually fix
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

## 🛠️ Quick Fix Commands

### Option 1: Use the Automated Fix Script
```bash
chmod +x fix-build.sh
./fix-build.sh
```

### Option 2: Manual Fix Steps

#### Step 1: Fix Frontend Dependencies
```bash
cd frontend

# Remove existing installations
rm -rf node_modules package-lock.json

# Install all dependencies
npm install

# Install specific missing dependencies
npm install @headlessui/react@1.7.17
npm install react-hot-toast@2.4.1
npm install @tanstack/react-query-devtools@5.8.4 --save-dev

# Test build
npm run build
```

#### Step 2: Fix Backend Dependencies
```bash
cd backend

# Create virtual environment if it doesn't exist
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### Step 3: Fix Docker Build
```bash
# Clean up Docker
docker-compose down
docker system prune -f

# Rebuild with no cache
docker-compose build --no-cache

# Start services
docker-compose up -d
```

## 🔍 Troubleshooting Specific Errors

### Error: `Can't resolve '@headlessui/react'`
```bash
cd frontend
npm install @headlessui/react@1.7.17
```

### Error: `Can't resolve 'react-hot-toast'`
```bash
cd frontend
npm install react-hot-toast@2.4.1
```

### Error: `Can't resolve '@tanstack/react-query-devtools'`
```bash
cd frontend
npm install @tanstack/react-query-devtools@5.8.4 --save-dev
```

### Error: Python module not found
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### Error: Database connection failed
```bash
# Make sure PostgreSQL is running
# Update your .env file with correct DATABASE_URL
cp .env.example .env
# Edit .env with your database credentials
```

### Error: Redis connection failed
```bash
# Make sure Redis is running
# Update your .env file with correct REDIS_URL
# Or use Docker: docker run -d -p 6379:6379 redis:6-alpine
```

## 🐳 Docker-Specific Fixes

### Fix 1: Update Dockerfile for Dependencies
The Dockerfile has been updated to install all dependencies including devDependencies during build.

### Fix 2: Use Standalone Output
Next.js is configured with `output: 'standalone'` for better Docker compatibility.

### Fix 3: Multi-stage Build
The Dockerfile uses multi-stage builds to optimize the final image size.

## 📋 Verification Steps

After applying fixes, verify everything works:

### 1. Test Frontend Build
```bash
cd frontend
npm run build
npm run start
```

### 2. Test Backend
```bash
cd backend
source venv/bin/activate
python -c "from app.main import app; print('Backend OK')"
uvicorn app.main:app --reload
```

### 3. Test Docker Build
```bash
docker-compose build
docker-compose up -d
```

### 4. Test Full System
```bash
./health-check.sh
```

## 🚀 Alternative Setup Methods

### Method 1: Use Setup Script
```bash
chmod +x setup.sh
./setup.sh
```

### Method 2: Manual Setup
```bash
# Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# Frontend
cd ../frontend
npm install
cp .env.example .env.local

# Database
createdb user_management
cd ../backend
alembic upgrade head
python -m app.db.init_db
```

### Method 3: Docker Setup
```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local
docker-compose up --build -d
docker-compose exec backend alembic upgrade head
docker-compose exec backend python -m app.db.init_db
```

## 🔧 Environment Configuration

### Backend (.env)
```env
DATABASE_URL=postgresql://user:password@localhost:5432/user_management
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-minimum-32-characters
DEBUG=true
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NODE_ENV=development
```

## 📞 Getting Help

If you're still experiencing issues:

1. **Check the logs**:
   ```bash
   # Docker logs
   docker-compose logs backend
   docker-compose logs frontend
   
   # Manual logs
   # Check terminal output for specific error messages
   ```

2. **Run health check**:
   ```bash
   ./health-check.sh
   ```

3. **Check system requirements**:
   - Python 3.9+
   - Node.js 18+
   - PostgreSQL 12+
   - Redis 6+

4. **Common solutions**:
   - Clear npm cache: `npm cache clean --force`
   - Clear pip cache: `pip cache purge`
   - Restart Docker: `docker-compose down && docker-compose up`
   - Check port conflicts: `lsof -i :3000` and `lsof -i :8000`

## ✅ Success Indicators

You'll know the build is successful when:

- ✅ Frontend builds without errors: `npm run build`
- ✅ Backend starts without errors: `uvicorn app.main:app`
- ✅ Docker containers start: `docker-compose up`
- ✅ Health check passes: `./health-check.sh`
- ✅ You can access:
  - Frontend: http://localhost:3000
  - Backend: http://localhost:8000
  - API Docs: http://localhost:8000/docs

## 🎉 All Fixed!

Once all issues are resolved, you can:

1. **Start the system**: `./start.sh`
2. **Run tests**: `./test.sh`
3. **Deploy**: `./deploy.sh`
4. **Upload to GitHub**: Follow `UPLOAD_TO_GITHUB.md`

The system is now ready for development and production use!
