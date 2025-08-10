# Deployment Guide

This guide covers deploying the User Management System in various environments.

## 🚀 Quick Start (Development)

### Prerequisites
- Python 3.9+
- Node.js 18+
- PostgreSQL 12+
- Redis 6+

### Backend Setup

1. **Clone and setup backend**
```bash
cd user-management-system/backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Environment configuration**
```bash
cp .env.example .env
# Edit .env with your database and Redis URLs
```

3. **Database setup**
```bash
# Create database
createdb user_management

# Run migrations
alembic upgrade head

# Initialize default data
python -m app.db.init_db
```

4. **Start backend**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

1. **Setup frontend**
```bash
cd user-management-system/frontend
npm install
```

2. **Environment configuration**
```bash
cp .env.example .env.local
# Edit .env.local with your API URL
```

3. **Start frontend**
```bash
npm run dev
```

### Access the Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Default Admin: admin@example.com / admin123

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)

1. **Clone repository**
```bash
git clone <repository-url>
cd user-management-system
```

2. **Configure environment**
```bash
# Copy and edit environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local

# Update backend/.env for production
DATABASE_URL=postgresql://user:password@db:5432/user_management
REDIS_URL=redis://redis:6379
DEBUG=false
SECRET_KEY=your-production-secret-key-minimum-32-characters
```

3. **Deploy with Docker Compose**
```bash
docker-compose up -d
```

4. **Initialize database**
```bash
# Run migrations
docker-compose exec backend alembic upgrade head

# Create initial admin user
docker-compose exec backend python -m app.db.init_db
```

### Individual Docker Containers

#### Backend
```bash
cd backend
docker build -t user-management-backend .
docker run -d \
  --name user-management-backend \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:password@host:5432/user_management \
  -e REDIS_URL=redis://host:6379 \
  user-management-backend
```

#### Frontend
```bash
cd frontend
docker build -t user-management-frontend .
docker run -d \
  --name user-management-frontend \
  -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=http://localhost:8000 \
  user-management-frontend
```

## ☁️ Cloud Deployment

### AWS Deployment

#### Using AWS ECS with Fargate

1. **Build and push images to ECR**
```bash
# Create ECR repositories
aws ecr create-repository --repository-name user-management-backend
aws ecr create-repository --repository-name user-management-frontend

# Get login token
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Build and push backend
cd backend
docker build -t user-management-backend .
docker tag user-management-backend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/user-management-backend:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/user-management-backend:latest

# Build and push frontend
cd ../frontend
docker build -t user-management-frontend .
docker tag user-management-frontend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/user-management-frontend:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/user-management-frontend:latest
```

2. **Setup RDS PostgreSQL**
```bash
aws rds create-db-instance \
  --db-instance-identifier user-management-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username admin \
  --master-user-password your-secure-password \
  --allocated-storage 20 \
  --vpc-security-group-ids sg-xxxxxxxx
```

3. **Setup ElastiCache Redis**
```bash
aws elasticache create-cache-cluster \
  --cache-cluster-id user-management-redis \
  --cache-node-type cache.t3.micro \
  --engine redis \
  --num-cache-nodes 1
```

4. **Create ECS Task Definition and Service**
```json
{
  "family": "user-management",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/user-management-backend:latest",
      "portMappings": [{"containerPort": 8000}],
      "environment": [
        {"name": "DATABASE_URL", "value": "postgresql://admin:password@rds-endpoint:5432/user_management"},
        {"name": "REDIS_URL", "value": "redis://elasticache-endpoint:6379"}
      ]
    },
    {
      "name": "frontend",
      "image": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/user-management-frontend:latest",
      "portMappings": [{"containerPort": 3000}],
      "environment": [
        {"name": "NEXT_PUBLIC_API_URL", "value": "https://api.yourdomain.com"}
      ]
    }
  ]
}
```

### Google Cloud Platform

#### Using Cloud Run

1. **Build and push to Container Registry**
```bash
# Configure Docker for GCP
gcloud auth configure-docker

# Build and push backend
cd backend
docker build -t gcr.io/your-project/user-management-backend .
docker push gcr.io/your-project/user-management-backend

# Build and push frontend
cd ../frontend
docker build -t gcr.io/your-project/user-management-frontend .
docker push gcr.io/your-project/user-management-frontend
```

2. **Deploy to Cloud Run**
```bash
# Deploy backend
gcloud run deploy user-management-backend \
  --image gcr.io/your-project/user-management-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DATABASE_URL=postgresql://user:pass@host/db,REDIS_URL=redis://host:6379

# Deploy frontend
gcloud run deploy user-management-frontend \
  --image gcr.io/your-project/user-management-frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars NEXT_PUBLIC_API_URL=https://backend-url
```

### DigitalOcean App Platform

1. **Create app.yaml**
```yaml
name: user-management-system
services:
- name: backend
  source_dir: /backend
  github:
    repo: your-username/user-management-system
    branch: main
  run_command: uvicorn app.main:app --host 0.0.0.0 --port 8080
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: DATABASE_URL
    value: ${db.DATABASE_URL}
  - key: REDIS_URL
    value: ${redis.DATABASE_URL}
  http_port: 8080

- name: frontend
  source_dir: /frontend
  github:
    repo: your-username/user-management-system
    branch: main
  run_command: npm start
  environment_slug: node-js
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: NEXT_PUBLIC_API_URL
    value: ${backend.PUBLIC_URL}
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
```

2. **Deploy**
```bash
doctl apps create --spec app.yaml
```

## 🔧 Production Configuration

### Environment Variables

#### Backend (.env)
```env
# Production settings
DEBUG=false
SECRET_KEY=your-production-secret-key-minimum-32-characters
DATABASE_URL=postgresql://user:password@host:5432/user_management
REDIS_URL=redis://host:6379

# Security
BACKEND_CORS_ORIGINS=["https://yourdomain.com"]
SESSION_COOKIE_SECURE=true

# Email (configure for production)
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=your-sendgrid-api-key
EMAILS_FROM_EMAIL=noreply@yourdomain.com
```

#### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NODE_ENV=production
```

### SSL/TLS Configuration

#### Using Let's Encrypt with Nginx

1. **Install Certbot**
```bash
sudo apt install certbot python3-certbot-nginx
```

2. **Nginx configuration**
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

3. **Obtain SSL certificate**
```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### Database Backup

#### Automated PostgreSQL Backup
```bash
#!/bin/bash
# backup.sh
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="user_management"

# Create backup
pg_dump $DB_NAME > $BACKUP_DIR/backup_$DATE.sql

# Compress backup
gzip $BACKUP_DIR/backup_$DATE.sql

# Remove backups older than 30 days
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete
```

#### Cron job for daily backups
```bash
# Add to crontab
0 2 * * * /path/to/backup.sh
```

### Monitoring and Logging

#### Using Docker Compose with Logging
```yaml
version: '3.8'
services:
  backend:
    # ... other config
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  frontend:
    # ... other config
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

#### Health Checks
```bash
# Backend health check
curl -f http://localhost:8000/health || exit 1

# Frontend health check
curl -f http://localhost:3000 || exit 1
```

## 🔒 Security Considerations

### Production Security Checklist

- [ ] Use strong, unique SECRET_KEY (minimum 32 characters)
- [ ] Enable HTTPS/SSL in production
- [ ] Configure proper CORS origins
- [ ] Use secure database credentials
- [ ] Enable database connection encryption
- [ ] Configure firewall rules
- [ ] Set up rate limiting
- [ ] Enable audit logging
- [ ] Configure secure session cookies
- [ ] Use environment variables for secrets
- [ ] Regular security updates
- [ ] Database backups
- [ ] Monitor for suspicious activity

### Firewall Configuration
```bash
# Allow SSH
sudo ufw allow ssh

# Allow HTTP and HTTPS
sudo ufw allow 80
sudo ufw allow 443

# Allow specific application ports (if needed)
sudo ufw allow 8000  # Backend (if not behind reverse proxy)
sudo ufw allow 3000  # Frontend (if not behind reverse proxy)

# Enable firewall
sudo ufw enable
```

## 📊 Performance Optimization

### Database Optimization
```sql
-- Add indexes for better performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);
CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);
```

### Redis Configuration
```redis
# redis.conf optimizations
maxmemory 256mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

### Frontend Optimization
```javascript
// next.config.js
module.exports = {
  output: 'standalone',
  compress: true,
  images: {
    formats: ['image/webp', 'image/avif'],
  },
  experimental: {
    optimizeCss: true,
  },
}
```

## 🚨 Troubleshooting

### Common Issues

#### Database Connection Issues
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check database connectivity
psql -h localhost -U user -d user_management -c "SELECT 1;"
```

#### Redis Connection Issues
```bash
# Check Redis status
sudo systemctl status redis

# Test Redis connectivity
redis-cli ping
```

#### Application Logs
```bash
# Backend logs
docker-compose logs backend

# Frontend logs
docker-compose logs frontend

# All logs
docker-compose logs -f
```

#### Performance Issues
```bash
# Check system resources
htop
df -h
free -h

# Check database performance
SELECT * FROM pg_stat_activity;
```

## 📞 Support

For deployment issues:
1. Check the logs for error messages
2. Verify environment variables are set correctly
3. Ensure all services are running
4. Check network connectivity between services
5. Review the troubleshooting section above

For additional help, please refer to the main README.md or create an issue in the repository.
