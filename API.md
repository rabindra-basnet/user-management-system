# API Documentation

This document provides comprehensive API documentation for the User Management System.

## 🚀 Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://api.yourdomain.com`

## 🔐 Authentication

### Authentication Methods

1. **JWT Bearer Token**: Primary authentication method
2. **API Key**: For programmatic access
3. **Session Cookie**: For web applications

### JWT Token Flow

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "is_active": true,
    "roles": [...]
  },
  "token": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "expires_in": 1800
  }
}
```

### Using Bearer Token

```http
GET /api/v1/users/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

## 📚 API Endpoints

### Authentication Endpoints

#### POST /api/v1/auth/login
Authenticate user and receive tokens.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "remember_me": false
}
```

**Response:** `200 OK`
```json
{
  "user": { ... },
  "token": { ... },
  "message": "Login successful"
}
```

#### POST /api/v1/auth/register
Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "password": "SecurePass123!",
  "confirm_password": "SecurePass123!"
}
```

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### POST /api/v1/auth/refresh
Refresh access token using refresh token.

**Request Body:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### POST /api/v1/auth/logout
Logout and invalidate tokens.

**Request Body:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response:** `200 OK`
```json
{
  "message": "Logged out successfully"
}
```

#### GET /api/v1/auth/me
Get current user information.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "roles": [
    {
      "id": "uuid",
      "name": "User",
      "permissions": [...]
    }
  ],
  "is_2fa_enabled": false,
  "last_login": "2024-01-01T00:00:00Z"
}
```

### User Management Endpoints

#### GET /api/v1/users/
List users with pagination and filtering.

**Query Parameters:**
- `skip` (int): Number of records to skip (default: 0)
- `limit` (int): Number of records to return (default: 100, max: 100)
- `search` (string): Search term for name or email
- `is_active` (boolean): Filter by active status

**Headers:** `Authorization: Bearer <token>`
**Required Permission:** `users.read`

**Response:** `200 OK`
```json
{
  "users": [
    {
      "id": "uuid",
      "email": "user@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "is_active": true,
      "roles": [...],
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 150,
  "page": 1,
  "size": 10,
  "pages": 15
}
```

#### POST /api/v1/users/
Create a new user.

**Headers:** `Authorization: Bearer <token>`
**Required Permission:** `users.create`

**Request Body:**
```json
{
  "email": "newuser@example.com",
  "first_name": "Jane",
  "last_name": "Smith",
  "password": "SecurePass123!",
  "confirm_password": "SecurePass123!",
  "is_active": true
}
```

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "email": "newuser@example.com",
  "first_name": "Jane",
  "last_name": "Smith",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### GET /api/v1/users/{user_id}
Get user by ID.

**Headers:** `Authorization: Bearer <token>`
**Required Permission:** `users.read` (or own profile)

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "roles": [...],
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### PUT /api/v1/users/{user_id}
Update user information.

**Headers:** `Authorization: Bearer <token>`
**Required Permission:** `users.update` (or own profile)

**Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+1234567890",
  "bio": "Updated bio"
}
```

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+1234567890",
  "bio": "Updated bio",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### DELETE /api/v1/users/{user_id}
Delete user account.

**Headers:** `Authorization: Bearer <token>`
**Required Permission:** `users.delete`

**Response:** `200 OK`
```json
{
  "message": "User deleted successfully"
}
```

### Role Management Endpoints

#### GET /api/v1/roles/
List all roles.

**Headers:** `Authorization: Bearer <token>`
**Required Permission:** `roles.read`

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "name": "Administrator",
    "description": "Full system access",
    "is_system_role": true,
    "permissions": [
      {
        "id": "uuid",
        "name": "users.create",
        "description": "Create users",
        "resource": "users",
        "action": "create"
      }
    ],
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

#### POST /api/v1/roles/
Create a new role.

**Headers:** `Authorization: Bearer <token>`
**Required Permission:** `roles.create`

**Request Body:**
```json
{
  "name": "Manager",
  "description": "Management role",
  "permission_ids": ["uuid1", "uuid2", "uuid3"]
}
```

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "name": "Manager",
  "description": "Management role",
  "permissions": [...],
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Permission Endpoints

#### GET /api/v1/permissions/
List all permissions.

**Headers:** `Authorization: Bearer <token>`
**Required Permission:** `permissions.read`

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "name": "users.create",
    "description": "Create users",
    "resource": "users",
    "action": "create",
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

### Admin Endpoints

#### GET /api/v1/admin/statistics
Get system statistics.

**Headers:** `Authorization: Bearer <token>`
**Required Permission:** `system.admin`

**Response:** `200 OK`
```json
{
  "total_users": 1250,
  "active_users": 1100,
  "inactive_users": 150,
  "verified_users": 1000,
  "users_with_2fa": 800,
  "total_roles": 5,
  "total_permissions": 25,
  "active_sessions": 450
}
```

#### GET /api/v1/admin/audit-logs
Get audit logs with filtering.

**Query Parameters:**
- `skip` (int): Pagination offset
- `limit` (int): Number of records
- `user_id` (uuid): Filter by user
- `action` (string): Filter by action
- `status` (string): Filter by status

**Headers:** `Authorization: Bearer <token>`
**Required Permission:** `audit.read`

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "user_id": "uuid",
    "action": "login_success",
    "resource": "auth",
    "ip_address": "192.168.1.1",
    "user_agent": "Mozilla/5.0...",
    "status": "success",
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

## 🔒 Two-Factor Authentication

### Setup 2FA

#### POST /api/v1/auth/2fa/setup
Initialize 2FA setup.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "secret": "JBSWY3DPEHPK3PXP",
  "qr_code": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
  "backup_codes": [
    "12345678",
    "87654321",
    "11223344"
  ]
}
```

#### POST /api/v1/auth/2fa/verify
Verify 2FA setup with TOTP code.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "code": "123456"
}
```

**Response:** `200 OK`
```json
{
  "message": "2FA enabled successfully"
}
```

## 📊 Error Responses

### Standard Error Format

```json
{
  "error": "Error Type",
  "message": "Human readable error message",
  "details": "Additional error details or validation errors",
  "status_code": 400
}
```

### Common HTTP Status Codes

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource conflict (e.g., email already exists)
- `422 Unprocessable Entity`: Validation errors
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

### Validation Errors

```json
{
  "error": "Validation Error",
  "message": "Invalid input data",
  "details": [
    {
      "loc": ["email"],
      "msg": "field required",
      "type": "value_error.missing"
    },
    {
      "loc": ["password"],
      "msg": "ensure this value has at least 8 characters",
      "type": "value_error.any_str.min_length"
    }
  ]
}
```

## 🔄 Rate Limiting

### Rate Limit Headers

All responses include rate limiting headers:

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

### Rate Limits by Endpoint

| Endpoint | Limit | Window |
|----------|-------|--------|
| `/auth/login` | 5 requests | 5 minutes |
| `/auth/register` | 3 requests | 1 hour |
| `/auth/refresh` | 10 requests | 5 minutes |
| `/users/*` (GET) | 100 requests | 5 minutes |
| `/users/*` (POST/PUT) | 50 requests | 5 minutes |
| `/admin/*` | 200 requests | 5 minutes |

## 📝 API Versioning

### Version Header

```http
Accept: application/vnd.api+json;version=1
```

### URL Versioning

```http
GET /api/v1/users/
GET /api/v2/users/  # Future version
```

## 🧪 Testing the API

### Using cURL

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "admin123"}'

# Get users (with token)
curl -X GET http://localhost:8000/api/v1/users/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# Create user
curl -X POST http://localhost:8000/api/v1/users/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "first_name": "New",
    "last_name": "User",
    "password": "SecurePass123!",
    "confirm_password": "SecurePass123!"
  }'
```

### Using Python Requests

```python
import requests

# Login
response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    json={
        "email": "admin@example.com",
        "password": "admin123"
    }
)
token = response.json()["token"]["access_token"]

# Get users
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(
    "http://localhost:8000/api/v1/users/",
    headers=headers
)
users = response.json()
```

### Using JavaScript/Fetch

```javascript
// Login
const loginResponse = await fetch('/api/v1/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    email: 'admin@example.com',
    password: 'admin123'
  })
});

const { token } = await loginResponse.json();

// Get users
const usersResponse = await fetch('/api/v1/users/', {
  headers: {
    'Authorization': `Bearer ${token.access_token}`
  }
});

const users = await usersResponse.json();
```

## 📖 Interactive Documentation

### Swagger UI
Visit `/docs` for interactive API documentation (development only).

### ReDoc
Visit `/redoc` for alternative API documentation (development only).

### OpenAPI Specification
Download the OpenAPI spec at `/openapi.json`.

## 🔧 SDK and Client Libraries

### Official SDKs
- **Python**: `pip install user-management-sdk`
- **JavaScript/TypeScript**: `npm install user-management-sdk`
- **Go**: `go get github.com/yourorg/user-management-go`

### Community SDKs
- **PHP**: Available on Packagist
- **Ruby**: Available as gem
- **Java**: Available on Maven Central

For more information, visit the [SDK documentation](https://docs.yourdomain.com/sdks).
