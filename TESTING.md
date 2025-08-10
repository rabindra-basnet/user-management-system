# Testing Guide

This guide covers testing procedures for the User Management System.

## 🧪 Test Categories

### 1. Unit Tests
- **Backend**: pytest for Python code
- **Frontend**: Jest for React components
- **Coverage**: Aim for >80% code coverage

### 2. Integration Tests
- API endpoint testing
- Database integration
- Authentication flows
- Permission validation

### 3. Security Tests
- Authentication bypass attempts
- Authorization escalation
- Input validation
- Rate limiting
- XSS/SQL injection protection

### 4. End-to-End Tests
- Complete user workflows
- Cross-browser compatibility
- Mobile responsiveness

## 🚀 Running Tests

### Backend Tests

```bash
cd backend

# Install test dependencies
pip install pytest pytest-cov pytest-asyncio

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_security.py

# Run specific test
pytest tests/test_auth.py::test_login_success
```

### Frontend Tests

```bash
cd frontend

# Install test dependencies
npm install --save-dev jest @testing-library/react @testing-library/jest-dom

# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run specific test file
npm test -- UserManagement.test.tsx

# Run tests in watch mode
npm test -- --watch
```

## 🔐 Security Testing

### Manual Security Tests

#### 1. Authentication Tests
```bash
# Test login with valid credentials
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "admin123"}'

# Test login with invalid credentials
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "wrong"}'

# Test token refresh
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "YOUR_REFRESH_TOKEN"}'
```

#### 2. Authorization Tests
```bash
# Test accessing protected endpoint without token
curl -X GET http://localhost:8000/api/v1/users/

# Test accessing protected endpoint with invalid token
curl -X GET http://localhost:8000/api/v1/users/ \
  -H "Authorization: Bearer invalid-token"

# Test accessing admin endpoint without admin permissions
curl -X GET http://localhost:8000/api/v1/admin/statistics \
  -H "Authorization: Bearer USER_TOKEN"
```

#### 3. Input Validation Tests
```bash
# Test SQL injection
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com'\'''; DROP TABLE users; --", "password": "test"}'

# Test XSS
curl -X POST http://localhost:8000/api/v1/users/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "first_name": "<script>alert(\"xss\")</script>", "last_name": "User", "password": "Test123!"}'
```

#### 4. Rate Limiting Tests
```bash
# Test rate limiting on login endpoint
for i in {1..10}; do
  curl -X POST http://localhost:8000/api/v1/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email": "test@example.com", "password": "wrong"}' &
done
wait
```

### Automated Security Testing

#### Using the Built-in Security Test Component

1. **Access Security Testing Page**
   - Navigate to http://localhost:3000/security
   - Click "Run Security Tests"
   - Review test results

2. **Custom Security Tests**
   - Use the custom input field to test specific payloads
   - Common test cases are provided in the interface

#### OWASP ZAP Integration
```bash
# Install OWASP ZAP
docker pull owasp/zap2docker-stable

# Run baseline scan
docker run -t owasp/zap2docker-stable zap-baseline.py -t http://localhost:3000

# Run full scan (takes longer)
docker run -t owasp/zap2docker-stable zap-full-scan.py -t http://localhost:3000
```

## 📊 Test Scenarios

### User Management Workflow Tests

#### 1. User Registration Flow
```javascript
// Test user registration
const registrationData = {
  email: 'newuser@example.com',
  first_name: 'New',
  last_name: 'User',
  password: 'SecurePass123!',
  confirm_password: 'SecurePass123!'
};

// Expected: 201 Created
// Verify: User created in database
// Verify: Email verification sent (if enabled)
```

#### 2. User Login Flow
```javascript
// Test successful login
const loginData = {
  email: 'admin@example.com',
  password: 'admin123'
};

// Expected: 200 OK with tokens
// Verify: Access token is valid
// Verify: Refresh token is valid
// Verify: User session created
```

#### 3. Password Change Flow
```javascript
// Test password change
const passwordData = {
  current_password: 'admin123',
  new_password: 'NewSecurePass123!',
  confirm_password: 'NewSecurePass123!'
};

// Expected: 200 OK
// Verify: Password updated in database
// Verify: All sessions invalidated except current
```

#### 4. 2FA Setup Flow
```javascript
// Test 2FA setup
// Step 1: Initiate 2FA setup
// Expected: QR code and secret returned

// Step 2: Verify with TOTP code
// Expected: 2FA enabled for user

// Step 3: Test login with 2FA
// Expected: 2FA code required after password
```

### Role and Permission Tests

#### 1. Role Creation
```javascript
// Test role creation
const roleData = {
  name: 'Test Manager',
  description: 'Test management role',
  permission_ids: ['perm1', 'perm2', 'perm3']
};

// Expected: 201 Created
// Verify: Role created with correct permissions
```

#### 2. Permission Assignment
```javascript
// Test assigning role to user
// Expected: User gains role permissions
// Verify: User can access permitted resources
// Verify: User cannot access non-permitted resources
```

### Admin Dashboard Tests

#### 1. Statistics Display
```javascript
// Test admin statistics endpoint
// Expected: Correct user counts
// Verify: Active/inactive user counts
// Verify: 2FA enabled counts
// Verify: Role and permission counts
```

#### 2. Audit Log Display
```javascript
// Test audit log retrieval
// Expected: Paginated audit logs
// Verify: Filtering by user works
// Verify: Filtering by action works
// Verify: Date sorting works
```

## 🔍 Performance Testing

### Load Testing with Artillery

```bash
# Install Artillery
npm install -g artillery

# Create test configuration
cat > load-test.yml << EOF
config:
  target: 'http://localhost:8000'
  phases:
    - duration: 60
      arrivalRate: 10
scenarios:
  - name: "Login flow"
    requests:
      - post:
          url: "/api/v1/auth/login"
          json:
            email: "admin@example.com"
            password: "admin123"
EOF

# Run load test
artillery run load-test.yml
```

### Database Performance Testing

```sql
-- Test query performance
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'test@example.com';

-- Test index usage
EXPLAIN ANALYZE SELECT * FROM audit_logs WHERE user_id = 'uuid' ORDER BY created_at DESC;

-- Monitor slow queries
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;
```

## 🐛 Debugging Tests

### Backend Debugging

```python
# Add debug logging to tests
import logging
logging.basicConfig(level=logging.DEBUG)

# Use pytest with verbose output
pytest -v -s tests/test_auth.py

# Debug specific test
pytest --pdb tests/test_auth.py::test_login_failure
```

### Frontend Debugging

```javascript
// Add debug output to tests
console.log('Test data:', testData);

// Use React Testing Library debug
import { render, screen } from '@testing-library/react';
const { debug } = render(<Component />);
debug(); // Prints DOM structure
```

### Database Debugging

```sql
-- Check test data
SELECT * FROM users WHERE email LIKE '%test%';

-- Check audit logs
SELECT * FROM audit_logs ORDER BY created_at DESC LIMIT 10;

-- Check active sessions
SELECT * FROM user_sessions WHERE is_active = true;
```

## 📋 Test Checklist

### Pre-deployment Testing

- [ ] All unit tests pass
- [ ] Integration tests pass
- [ ] Security tests pass
- [ ] Performance tests meet requirements
- [ ] Cross-browser testing completed
- [ ] Mobile responsiveness verified
- [ ] Database migrations tested
- [ ] Backup and restore tested
- [ ] Error handling tested
- [ ] Logging functionality verified

### Security Testing Checklist

- [ ] Authentication bypass attempts fail
- [ ] Authorization escalation attempts fail
- [ ] SQL injection attempts blocked
- [ ] XSS attempts sanitized
- [ ] CSRF protection working
- [ ] Rate limiting enforced
- [ ] Session management secure
- [ ] Password policies enforced
- [ ] 2FA working correctly
- [ ] Audit logging complete

### User Experience Testing

- [ ] Registration flow works
- [ ] Login flow works
- [ ] Password reset works
- [ ] Profile updates work
- [ ] Role assignments work
- [ ] Permission checks work
- [ ] Dashboard loads correctly
- [ ] Search functionality works
- [ ] Pagination works
- [ ] Error messages clear

## 🚨 Troubleshooting Tests

### Common Test Issues

#### Backend Test Failures
```bash
# Database connection issues
export DATABASE_URL="postgresql://test_user:test_pass@localhost/test_db"

# Redis connection issues
export REDIS_URL="redis://localhost:6379/1"

# Permission issues
chmod +x scripts/run-tests.sh
```

#### Frontend Test Failures
```bash
# Clear Jest cache
npm test -- --clearCache

# Update snapshots
npm test -- --updateSnapshot

# Run tests with more memory
node --max-old-space-size=4096 node_modules/.bin/jest
```

#### Security Test Issues
```bash
# Check if security middleware is enabled
curl -I http://localhost:8000/health

# Verify rate limiting is working
curl -w "%{http_code}" http://localhost:8000/api/v1/auth/login

# Check CORS headers
curl -H "Origin: http://malicious-site.com" http://localhost:8000/api/v1/users/
```

## 📊 Test Reports

### Coverage Reports

```bash
# Backend coverage
pytest --cov=app --cov-report=html
open htmlcov/index.html

# Frontend coverage
npm run test:coverage
open coverage/lcov-report/index.html
```

### Security Reports

```bash
# Generate security report
python scripts/security-audit.py > security-report.txt

# OWASP ZAP report
docker run -v $(pwd):/zap/wrk/:rw -t owasp/zap2docker-stable zap-baseline.py \
  -t http://localhost:3000 -r security-report.html
```

## 🔄 Continuous Testing

### GitHub Actions Integration

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: pip install -r backend/requirements.txt
      - name: Run tests
        run: cd backend && pytest --cov=app

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Node.js
        uses: actions/setup-node@v2
        with:
          node-version: 18
      - name: Install dependencies
        run: cd frontend && npm install
      - name: Run tests
        run: cd frontend && npm test
```

For more detailed testing procedures, refer to the individual test files in the `tests/` directories.
