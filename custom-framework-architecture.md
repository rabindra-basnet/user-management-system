# Custom Framework Architecture Design
## Inspired by Frappe's Design Patterns

This document outlines a comprehensive architecture for building a custom application framework that captures the key design patterns and features of Frappe while being built from scratch for closed-source purposes.

## Technology Stack

### Backend Options
- **Python**: FastAPI + SQLAlchemy + Pydantic
- **Go**: Gin/Echo + GORM + Validator
- **Database**: PostgreSQL (primary) / MySQL (alternative)
- **Cache**: Redis
- **Queue**: Celery (Python) / Asynq (Go)

### Frontend
- **TypeScript**: React/Vue.js + TanStack Query
- **UI Framework**: Tailwind CSS + Headless UI
- **State Management**: Zustand/Pinia
- **Build Tool**: Vite

## Core Architecture Principles

### 1. Document-Centric Design
Everything is a "Document" (similar to Frappe's DocType):
- Users, Roles, Permissions are documents
- Business entities (Orders, Customers, etc.) are documents
- Configuration and settings are documents

### 2. Metadata-Driven Development
- Schema definitions drive UI generation
- Field types determine validation and rendering
- Permissions are metadata-driven

### 3. Event-Driven Architecture
- Document lifecycle hooks
- Background job processing
- Real-time notifications

### 4. Modular Organization
- Feature-based modules
- Plugin architecture
- Clean separation of concerns

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (TypeScript)                    │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Admin UI  │  │  Forms UI   │  │  Reports    │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │           API Client & State Management             │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                         HTTP/WebSocket
                              │
┌─────────────────────────────────────────────────────────────┐
│                  API Gateway / Load Balancer                │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    Backend Services                         │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Auth      │  │   Core      │  │  Business   │         │
│  │  Service    │  │  Service    │  │  Services   │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              Shared Libraries                       │ │
│  │  • Document Engine  • Permission Engine             │ │
│  │  • Validation       • Event System                  │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    Data Layer                               │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ PostgreSQL  │  │    Redis    │  │   File      │         │
│  │ (Primary)   │  │   (Cache)   │  │  Storage    │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                Background Processing                        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Queue     │  │  Scheduler  │  │   Workers   │         │
│  │  (Redis)    │  │   (Cron)    │  │ (Celery/Go) │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Document Engine
The heart of the system - manages all entities as documents with:
- Schema definition and validation
- CRUD operations with hooks
- Relationship management
- Version control and audit trails

### 2. Permission Engine
Comprehensive access control system:
- Role-based permissions
- Document-level permissions
- Field-level permissions
- Dynamic permission evaluation

### 3. Event System
Handles all system events:
- Document lifecycle events
- Background job scheduling
- Real-time notifications
- Webhook integrations

### 4. API Layer
RESTful API with:
- Auto-generated endpoints from schemas
- Custom business logic endpoints
- Real-time WebSocket connections
- API versioning and documentation

### 5. Module System
Organized feature modules:
- Core modules (User, Role, Permission)
- Business modules (customizable)
- Plugin architecture for extensions

## Key Features to Implement

### Phase 1: Foundation
1. **Document Schema System**
2. **Basic CRUD Operations**
3. **User Authentication**
4. **Role-based Permissions**
5. **API Framework**

### Phase 2: Advanced Features
1. **Document Relationships**
2. **Field-level Permissions**
3. **Event Hooks System**
4. **Background Jobs**
5. **File Management**

### Phase 3: Business Features
1. **Workflow Engine**
2. **Reporting System**
3. **Notification System**
4. **Audit Trails**
5. **Plugin Architecture**

## Document System Design

### Schema Definition Structure

The document system uses JSON schema definitions similar to Frappe's DocType JSON files:

```json
{
  "name": "User",
  "module": "core",
  "label": "User",
  "description": "System user with authentication and permissions",
  "naming_rule": "field:email",
  "is_submittable": false,
  "is_tree": false,
  "track_changes": true,
  "fields": [
    {
      "fieldname": "email",
      "fieldtype": "Email",
      "label": "Email Address",
      "required": true,
      "unique": true,
      "in_list_view": true,
      "in_standard_filter": true
    },
    {
      "fieldname": "first_name",
      "fieldtype": "Data",
      "label": "First Name",
      "required": true,
      "in_list_view": true,
      "max_length": 50
    },
    {
      "fieldname": "last_name",
      "fieldtype": "Data",
      "label": "Last Name",
      "required": false,
      "in_list_view": true,
      "max_length": 50
    },
    {
      "fieldname": "full_name",
      "fieldtype": "Data",
      "label": "Full Name",
      "read_only": true,
      "in_global_search": true
    },
    {
      "fieldname": "roles",
      "fieldtype": "Table",
      "label": "Roles",
      "options": "UserRole",
      "description": "Roles assigned to this user"
    },
    {
      "fieldname": "is_active",
      "fieldtype": "Check",
      "label": "Active",
      "default": true,
      "in_list_view": true,
      "in_standard_filter": true
    },
    {
      "fieldname": "last_login",
      "fieldtype": "Datetime",
      "label": "Last Login",
      "read_only": true
    }
  ],
  "permissions": [
    {
      "role": "System Administrator",
      "read": true,
      "write": true,
      "create": true,
      "delete": true
    },
    {
      "role": "User Manager",
      "read": true,
      "write": true,
      "create": true,
      "delete": false
    }
  ],
  "hooks": {
    "before_save": ["validate_email", "set_full_name"],
    "after_insert": ["send_welcome_email", "setup_default_permissions"],
    "on_update": ["clear_user_cache"],
    "before_delete": ["check_dependencies"]
  }
}
```

### Field Types System

```typescript
// Field type definitions
export enum FieldType {
  // Basic Types
  DATA = "Data",
  TEXT = "Text",
  LONG_TEXT = "LongText",
  EMAIL = "Email",
  PHONE = "Phone",
  URL = "URL",

  // Numeric Types
  INT = "Int",
  FLOAT = "Float",
  CURRENCY = "Currency",
  PERCENT = "Percent",

  // Date/Time Types
  DATE = "Date",
  DATETIME = "Datetime",
  TIME = "Time",

  // Selection Types
  SELECT = "Select",
  CHECK = "Check",

  // Relationship Types
  LINK = "Link",
  DYNAMIC_LINK = "DynamicLink",
  TABLE = "Table",

  // File Types
  ATTACH = "Attach",
  ATTACH_IMAGE = "AttachImage",

  // Special Types
  JSON = "JSON",
  CODE = "Code",
  HTML = "HTML",
  MARKDOWN = "Markdown"
}

export interface FieldDefinition {
  fieldname: string;
  fieldtype: FieldType;
  label: string;
  required?: boolean;
  unique?: boolean;
  default?: any;
  options?: string; // For Link, Select fields
  max_length?: number;
  precision?: number;
  read_only?: boolean;
  hidden?: boolean;
  depends_on?: string; // Conditional display
  mandatory_depends_on?: string;
  in_list_view?: boolean;
  in_standard_filter?: boolean;
  in_global_search?: boolean;
  description?: string;
  help_text?: string;
}
```

### Document Base Class

```python
# Python implementation
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

class BaseDocument(ABC):
    def __init__(self, data: Dict[str, Any] = None):
        self._data = data or {}
        self._original_data = {}
        self._meta = self.get_meta()
        self._is_new = True
        self._hooks_executed = set()

    @classmethod
    @abstractmethod
    def get_meta(cls) -> 'DocumentMeta':
        """Return document metadata"""
        pass

    def __getattr__(self, name: str) -> Any:
        if name in self._data:
            return self._data[name]
        return None

    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith('_'):
            super().__setattr__(name, value)
        else:
            self._data[name] = value

    def get(self, fieldname: str, default: Any = None) -> Any:
        """Get field value with default"""
        return self._data.get(fieldname, default)

    def set(self, fieldname: str, value: Any) -> None:
        """Set field value"""
        self._data[fieldname] = value

    def validate(self) -> None:
        """Validate document data"""
        self._validate_required_fields()
        self._validate_field_types()
        self._validate_unique_fields()
        self._run_custom_validations()

    def save(self) -> 'BaseDocument':
        """Save document to database"""
        self._run_before_save_hooks()
        self.validate()

        if self._is_new:
            self._insert()
            self._run_after_insert_hooks()
        else:
            self._update()
            self._run_on_update_hooks()

        self._run_after_save_hooks()
        return self

    def delete(self) -> None:
        """Delete document"""
        self._run_before_delete_hooks()
        self._delete_from_db()
        self._run_after_delete_hooks()

    def _validate_required_fields(self) -> None:
        """Validate required fields"""
        for field in self._meta.fields:
            if field.required and not self.get(field.fieldname):
                raise ValidationError(f"{field.label} is required")

    def _run_before_save_hooks(self) -> None:
        """Execute before_save hooks"""
        hooks = self._meta.hooks.get('before_save', [])
        for hook in hooks:
            getattr(self, hook)()
```

### Document Registry and Factory

```python
class DocumentRegistry:
    """Registry for all document types"""
    _documents: Dict[str, type] = {}

    @classmethod
    def register(cls, doctype: str, document_class: type) -> None:
        """Register a document class"""
        cls._documents[doctype] = document_class

    @classmethod
    def get_document_class(cls, doctype: str) -> type:
        """Get document class by doctype"""
        if doctype not in cls._documents:
            raise ValueError(f"Document type '{doctype}' not registered")
        return cls._documents[doctype]

    @classmethod
    def create_document(cls, doctype: str, data: Dict[str, Any] = None) -> BaseDocument:
        """Create document instance"""
        document_class = cls.get_document_class(doctype)
        return document_class(data)

# Usage
@DocumentRegistry.register("User")
class User(BaseDocument):
    @classmethod
    def get_meta(cls):
        return load_document_meta("User")

    def validate_email(self):
        """Custom validation for email"""
        if not self.email or '@' not in self.email:
            raise ValidationError("Invalid email address")

    def set_full_name(self):
        """Set full name from first and last name"""
        parts = [self.first_name, self.last_name]
        self.full_name = " ".join(filter(None, parts))
```

This document system provides:
- **Flexible Schema Definition**: JSON-based schema similar to Frappe
- **Type Safety**: Strong typing for fields and validation
- **Extensible Hooks**: Lifecycle hooks for custom business logic
- **Automatic CRUD**: Generated database operations
- **Validation Framework**: Built-in and custom validation rules

## Permission & Role System Design

### Role-Based Access Control (RBAC)

The permission system follows a hierarchical model similar to Frappe:

```json
{
  "name": "Role",
  "fields": [
    {
      "fieldname": "role_name",
      "fieldtype": "Data",
      "label": "Role Name",
      "required": true,
      "unique": true
    },
    {
      "fieldname": "description",
      "fieldtype": "Text",
      "label": "Description"
    },
    {
      "fieldname": "is_system_role",
      "fieldtype": "Check",
      "label": "System Role",
      "default": false,
      "read_only": true
    },
    {
      "fieldname": "permissions",
      "fieldtype": "Table",
      "label": "Document Permissions",
      "options": "RolePermission"
    }
  ]
}
```

### Permission Matrix Structure

```typescript
export interface Permission {
  doctype: string;
  role: string;
  read: boolean;
  write: boolean;
  create: boolean;
  delete: boolean;
  submit?: boolean;
  cancel?: boolean;
  amend?: boolean;
  report: boolean;
  export: boolean;
  import: boolean;
  share: boolean;
  print: boolean;
  email: boolean;
  if_owner: boolean;
  permission_level: number;
  conditions?: string; // SQL-like conditions
}

export interface FieldPermission {
  doctype: string;
  fieldname: string;
  role: string;
  read: boolean;
  write: boolean;
  permission_level: number;
}

export interface UserPermission {
  user: string;
  allow_doctype: string;
  allow_value: string;
  applicable_for?: string; // Specific doctype this applies to
  is_default: boolean;
}
```

### Permission Engine Implementation

```python
from typing import List, Dict, Any, Optional
from enum import Enum

class PermissionType(Enum):
    READ = "read"
    WRITE = "write"
    CREATE = "create"
    DELETE = "delete"
    SUBMIT = "submit"
    CANCEL = "cancel"
    REPORT = "report"
    EXPORT = "export"
    IMPORT = "import"
    SHARE = "share"
    PRINT = "print"
    EMAIL = "email"

class PermissionEngine:
    def __init__(self, db_session, cache_manager):
        self.db = db_session
        self.cache = cache_manager

    def has_permission(
        self,
        user: str,
        doctype: str,
        permission_type: PermissionType,
        doc: Optional[BaseDocument] = None,
        permission_level: int = 0
    ) -> bool:
        """Check if user has permission for doctype/document"""

        # System Administrator has all permissions
        if self._is_system_administrator(user):
            return True

        # Get user roles
        user_roles = self._get_user_roles(user)
        if not user_roles:
            return False

        # Check role-based permissions
        role_permissions = self._get_role_permissions(
            doctype, user_roles, permission_level
        )

        # Check if any role has the required permission
        has_role_permission = any(
            perm.get(permission_type.value, False)
            for perm in role_permissions
        )

        if not has_role_permission:
            return False

        # If checking specific document
        if doc:
            # Check owner permissions
            if self._check_owner_permission(user, doc, role_permissions):
                return True

            # Check user-specific permissions
            if self._check_user_permissions(user, doc):
                return True

            # Check share permissions
            if self._check_share_permissions(user, doc):
                return True

            # Check conditional permissions
            if self._check_conditional_permissions(user, doc, role_permissions):
                return True

        return has_role_permission

    def get_permitted_documents(
        self,
        user: str,
        doctype: str,
        permission_type: PermissionType = PermissionType.READ,
        filters: Dict[str, Any] = None
    ) -> List[str]:
        """Get list of document names user can access"""

        if self._is_system_administrator(user):
            # Admin can access all documents
            return self._get_all_document_names(doctype, filters)

        user_roles = self._get_user_roles(user)
        role_permissions = self._get_role_permissions(doctype, user_roles)

        # Build query conditions based on permissions
        conditions = []

        # Owner condition
        if any(perm.get('if_owner') for perm in role_permissions):
            conditions.append(f"owner = '{user}'")

        # User permissions
        user_perms = self._get_user_permissions(user, doctype)
        if user_perms:
            perm_conditions = [
                f"{perm['field']} = '{perm['value']}'"
                for perm in user_perms
            ]
            conditions.extend(perm_conditions)

        # Shared documents
        shared_docs = self._get_shared_documents(user, doctype)
        if shared_docs:
            conditions.append(f"name IN ({','.join(shared_docs)})")

        # Custom conditions from role permissions
        for perm in role_permissions:
            if perm.get('conditions'):
                conditions.append(perm['conditions'])

        return self._query_documents_with_conditions(doctype, conditions, filters)

    def check_field_permission(
        self,
        user: str,
        doctype: str,
        fieldname: str,
        permission_type: PermissionType,
        permission_level: int = 0
    ) -> bool:
        """Check field-level permissions"""

        # Get field permissions for user roles
        user_roles = self._get_user_roles(user)
        field_perms = self._get_field_permissions(
            doctype, fieldname, user_roles, permission_level
        )

        return any(
            perm.get(permission_type.value, True)
            for perm in field_perms
        )

    def add_user_permission(
        self,
        user: str,
        allow_doctype: str,
        allow_value: str,
        applicable_for: str = None
    ) -> None:
        """Add user-specific permission"""
        user_perm = {
            'user': user,
            'allow_doctype': allow_doctype,
            'allow_value': allow_value,
            'applicable_for': applicable_for,
            'is_default': False
        }
        self.db.insert('user_permission', user_perm)
        self._clear_user_permission_cache(user)

    def share_document(
        self,
        doctype: str,
        docname: str,
        user: str,
        permissions: Dict[str, bool]
    ) -> None:
        """Share document with specific user"""
        share_data = {
            'doctype': doctype,
            'docname': docname,
            'user': user,
            'read': permissions.get('read', True),
            'write': permissions.get('write', False),
            'share': permissions.get('share', False)
        }
        self.db.insert('document_share', share_data)
        self._clear_share_cache(user, doctype)

    def _get_user_roles(self, user: str) -> List[str]:
        """Get roles assigned to user"""
        cache_key = f"user_roles:{user}"
        roles = self.cache.get(cache_key)

        if roles is None:
            roles = self.db.query(
                "SELECT role FROM user_role WHERE user = %s", [user]
            )
            self.cache.set(cache_key, roles, ttl=300)  # 5 minutes

        return roles

    def _check_owner_permission(
        self,
        user: str,
        doc: BaseDocument,
        role_permissions: List[Dict]
    ) -> bool:
        """Check if user is owner and has owner permissions"""
        if doc.get('owner') != user:
            return False

        return any(perm.get('if_owner', False) for perm in role_permissions)
```

### Permission Decorators and Middleware

```python
from functools import wraps
from flask import request, g

def requires_permission(doctype: str, permission_type: PermissionType):
    """Decorator to check permissions for API endpoints"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = g.current_user
            if not permission_engine.has_permission(user, doctype, permission_type):
                raise PermissionError(f"No {permission_type.value} permission for {doctype}")
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def requires_doc_permission(permission_type: PermissionType):
    """Decorator to check permissions for specific document"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            doctype = kwargs.get('doctype')
            docname = kwargs.get('docname')

            if doctype and docname:
                doc = get_document(doctype, docname)
                user = g.current_user

                if not permission_engine.has_permission(
                    user, doctype, permission_type, doc
                ):
                    raise PermissionError(
                        f"No {permission_type.value} permission for {doctype} {docname}"
                    )

            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Usage in API endpoints
@app.route('/api/user', methods=['POST'])
@requires_permission('User', PermissionType.CREATE)
def create_user():
    # Create user logic
    pass

@app.route('/api/user/<docname>', methods=['GET'])
@requires_doc_permission(PermissionType.READ)
def get_user(docname):
    # Get user logic
    pass
```

This permission system provides:
- **Hierarchical Roles**: Role-based access control with inheritance
- **Document-level Permissions**: Fine-grained control per document
- **Field-level Permissions**: Control access to specific fields
- **User Permissions**: User-specific access restrictions
- **Share Permissions**: Document sharing capabilities
- **Conditional Permissions**: Dynamic permission evaluation
- **Performance Optimized**: Caching and efficient queries

## API Architecture Design

### RESTful API Structure

The API follows REST principles with auto-generated endpoints based on document schemas:

```
Base URL: https://api.yourapp.com/v1

Authentication:
POST   /auth/login
POST   /auth/logout
POST   /auth/refresh
GET    /auth/me

Document Operations:
GET    /api/doctype/{doctype}                    # List documents
POST   /api/doctype/{doctype}                    # Create document
GET    /api/doctype/{doctype}/{name}             # Get document
PUT    /api/doctype/{doctype}/{name}             # Update document
DELETE /api/doctype/{doctype}/{name}             # Delete document
PATCH  /api/doctype/{doctype}/{name}             # Partial update

Document Methods:
POST   /api/doctype/{doctype}/{name}/method/{method_name}

Custom Methods:
POST   /api/method/{method_path}

File Operations:
POST   /api/files/upload
GET    /api/files/{file_id}
DELETE /api/files/{file_id}

Metadata:
GET    /api/meta/{doctype}                       # Get doctype metadata
GET    /api/meta/{doctype}/permissions           # Get permissions

Real-time:
WS     /ws/updates                               # WebSocket for real-time updates
```

### API Implementation (Python/FastAPI)

```python
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.security import HTTPBearer
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import json

app = FastAPI(title="Custom Framework API", version="1.0.0")
security = HTTPBearer()

class DocumentResponse(BaseModel):
    name: str
    data: Dict[str, Any]
    meta: Dict[str, Any]

class ListResponse(BaseModel):
    data: List[Dict[str, Any]]
    total_count: int
    page: int
    page_size: int
    has_next: bool

class APIError(BaseModel):
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None

# Dependency to get current user
async def get_current_user(token: str = Depends(security)):
    try:
        user = auth_service.verify_token(token.credentials)
        return user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

# Auto-generated CRUD endpoints
@app.get("/api/doctype/{doctype}", response_model=ListResponse)
async def list_documents(
    doctype: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    fields: Optional[str] = Query(None),
    filters: Optional[str] = Query(None),
    order_by: Optional[str] = Query(None),
    current_user: str = Depends(get_current_user)
):
    """List documents with filtering and pagination"""

    # Check read permission
    if not permission_engine.has_permission(current_user, doctype, PermissionType.READ):
        raise HTTPException(status_code=403, detail="No read permission")

    # Parse query parameters
    field_list = json.loads(fields) if fields else None
    filter_dict = json.loads(filters) if filters else {}

    # Get permitted documents
    permitted_docs = permission_engine.get_permitted_documents(
        current_user, doctype, PermissionType.READ, filter_dict
    )

    # Apply pagination
    offset = (page - 1) * page_size
    documents = document_service.get_list(
        doctype=doctype,
        fields=field_list,
        filters=filter_dict,
        order_by=order_by,
        limit=page_size,
        offset=offset,
        permitted_names=permitted_docs
    )

    total_count = document_service.get_count(doctype, filter_dict, permitted_docs)

    return ListResponse(
        data=documents,
        total_count=total_count,
        page=page,
        page_size=page_size,
        has_next=total_count > page * page_size
    )

@app.post("/api/doctype/{doctype}", response_model=DocumentResponse)
async def create_document(
    doctype: str,
    data: Dict[str, Any],
    current_user: str = Depends(get_current_user)
):
    """Create new document"""

    # Check create permission
    if not permission_engine.has_permission(current_user, doctype, PermissionType.CREATE):
        raise HTTPException(status_code=403, detail="No create permission")

    try:
        # Create document
        doc = document_service.create(doctype, data, current_user)

        # Return response
        return DocumentResponse(
            name=doc.name,
            data=doc.as_dict(),
            meta=doc.get_meta().as_dict()
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/doctype/{doctype}/{name}", response_model=DocumentResponse)
async def get_document(
    doctype: str,
    name: str,
    current_user: str = Depends(get_current_user)
):
    """Get specific document"""

    try:
        doc = document_service.get(doctype, name)

        # Check read permission for specific document
        if not permission_engine.has_permission(
            current_user, doctype, PermissionType.READ, doc
        ):
            raise HTTPException(status_code=403, detail="No read permission")

        # Filter fields based on field-level permissions
        filtered_data = {}
        for field_name, value in doc.as_dict().items():
            if permission_engine.check_field_permission(
                current_user, doctype, field_name, PermissionType.READ
            ):
                filtered_data[field_name] = value

        return DocumentResponse(
            name=doc.name,
            data=filtered_data,
            meta=doc.get_meta().as_dict()
        )
    except DocumentNotFoundError:
        raise HTTPException(status_code=404, detail="Document not found")

@app.put("/api/doctype/{doctype}/{name}", response_model=DocumentResponse)
async def update_document(
    doctype: str,
    name: str,
    data: Dict[str, Any],
    current_user: str = Depends(get_current_user)
):
    """Update document"""

    try:
        doc = document_service.get(doctype, name)

        # Check write permission
        if not permission_engine.has_permission(
            current_user, doctype, PermissionType.WRITE, doc
        ):
            raise HTTPException(status_code=403, detail="No write permission")

        # Check field-level write permissions
        for field_name in data.keys():
            if not permission_engine.check_field_permission(
                current_user, doctype, field_name, PermissionType.WRITE
            ):
                raise HTTPException(
                    status_code=403,
                    detail=f"No write permission for field {field_name}"
                )

        # Update document
        updated_doc = document_service.update(doc, data, current_user)

        return DocumentResponse(
            name=updated_doc.name,
            data=updated_doc.as_dict(),
            meta=updated_doc.get_meta().as_dict()
        )
    except DocumentNotFoundError:
        raise HTTPException(status_code=404, detail="Document not found")
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/api/doctype/{doctype}/{name}")
async def delete_document(
    doctype: str,
    name: str,
    current_user: str = Depends(get_current_user)
):
    """Delete document"""

    try:
        doc = document_service.get(doctype, name)

        # Check delete permission
        if not permission_engine.has_permission(
            current_user, doctype, PermissionType.DELETE, doc
        ):
            raise HTTPException(status_code=403, detail="No delete permission")

        document_service.delete(doc, current_user)
        return {"message": "Document deleted successfully"}
    except DocumentNotFoundError:
        raise HTTPException(status_code=404, detail="Document not found")

# Custom method execution
@app.post("/api/doctype/{doctype}/{name}/method/{method_name}")
async def execute_document_method(
    doctype: str,
    name: str,
    method_name: str,
    args: Dict[str, Any] = {},
    current_user: str = Depends(get_current_user)
):
    """Execute custom method on document"""

    try:
        doc = document_service.get(doctype, name)

        # Check if method is whitelisted
        if not document_service.is_method_whitelisted(doctype, method_name):
            raise HTTPException(status_code=403, detail="Method not allowed")

        # Check method permission (usually write)
        if not permission_engine.has_permission(
            current_user, doctype, PermissionType.WRITE, doc
        ):
            raise HTTPException(status_code=403, detail="No permission to execute method")

        # Execute method
        result = document_service.execute_method(doc, method_name, args, current_user)

        return {
            "message": "Method executed successfully",
            "result": result,
            "doc": doc.as_dict()
        }
    except DocumentNotFoundError:
        raise HTTPException(status_code=404, detail="Document not found")
    except MethodNotFoundError:
        raise HTTPException(status_code=404, detail="Method not found")
```

This API architecture provides:
- **Auto-generated Endpoints**: CRUD operations based on document schemas
- **Permission Integration**: Built-in permission checking
- **Field-level Security**: Filtering based on field permissions
- **Validation**: Automatic validation using document schemas
- **Error Handling**: Consistent error responses
- **Documentation**: Auto-generated API documentation with FastAPI

## Module Organization Design

### Project Structure

```
your-framework/
├── backend/
│   ├── core/                          # Core framework modules
│   │   ├── __init__.py
│   │   ├── document/                  # Document engine
│   │   │   ├── __init__.py
│   │   │   ├── base.py               # BaseDocument class
│   │   │   ├── registry.py           # Document registry
│   │   │   ├── meta.py               # Document metadata
│   │   │   └── validation.py         # Validation engine
│   │   ├── permissions/               # Permission system
│   │   │   ├── __init__.py
│   │   │   ├── engine.py             # Permission engine
│   │   │   ├── roles.py              # Role management
│   │   │   └── decorators.py         # Permission decorators
│   │   ├── api/                       # API framework
│   │   │   ├── __init__.py
│   │   │   ├── router.py             # Auto-generated routes
│   │   │   ├── middleware.py         # API middleware
│   │   │   └── responses.py          # Response models
│   │   ├── auth/                      # Authentication
│   │   │   ├── __init__.py
│   │   │   ├── jwt.py                # JWT handling
│   │   │   ├── providers.py          # Auth providers
│   │   │   └── middleware.py         # Auth middleware
│   │   ├── database/                  # Database layer
│   │   │   ├── __init__.py
│   │   │   ├── connection.py         # DB connection
│   │   │   ├── migrations.py         # Migration system
│   │   │   └── query_builder.py      # Query builder
│   │   ├── cache/                     # Caching system
│   │   │   ├── __init__.py
│   │   │   ├── redis.py              # Redis cache
│   │   │   └── memory.py             # In-memory cache
│   │   ├── events/                    # Event system
│   │   │   ├── __init__.py
│   │   │   ├── emitter.py            # Event emitter
│   │   │   ├── hooks.py              # Hook system
│   │   │   └── background.py         # Background jobs
│   │   └── utils/                     # Utilities
│   │       ├── __init__.py
│   │       ├── validation.py         # Validation helpers
│   │       ├── formatting.py         # Data formatting
│   │       └── security.py           # Security utilities
│   ├── modules/                       # Business modules
│   │   ├── __init__.py
│   │   ├── user_management/           # User management module
│   │   │   ├── __init__.py
│   │   │   ├── models/               # Document definitions
│   │   │   │   ├── user.py
│   │   │   │   ├── role.py
│   │   │   │   └── user_role.py
│   │   │   ├── controllers/          # Business logic
│   │   │   │   ├── user_controller.py
│   │   │   │   └── auth_controller.py
│   │   │   ├── services/             # Service layer
│   │   │   │   ├── user_service.py
│   │   │   │   └── auth_service.py
│   │   │   ├── api/                  # Module-specific APIs
│   │   │   │   ├── user_routes.py
│   │   │   │   └── auth_routes.py
│   │   │   └── schemas/              # JSON schemas
│   │   │       ├── user.json
│   │   │       ├── role.json
│   │   │       └── user_role.json
│   │   ├── file_management/           # File management module
│   │   │   ├── models/
│   │   │   ├── controllers/
│   │   │   ├── services/
│   │   │   └── api/
│   │   └── workflow/                  # Workflow module
│   │       ├── models/
│   │       ├── controllers/
│   │       ├── services/
│   │       └── api/
│   ├── config/                        # Configuration
│   │   ├── __init__.py
│   │   ├── settings.py               # Application settings
│   │   ├── database.py               # Database config
│   │   └── logging.py                # Logging config
│   ├── migrations/                    # Database migrations
│   ├── tests/                         # Test suite
│   │   ├── unit/
│   │   ├── integration/
│   │   └── fixtures/
│   ├── main.py                        # Application entry point
│   └── requirements.txt               # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── core/                      # Core frontend framework
│   │   │   ├── api/                  # API client
│   │   │   ├── auth/                 # Authentication
│   │   │   ├── permissions/          # Permission checking
│   │   │   ├── forms/                # Form generation
│   │   │   ├── tables/               # Table/list views
│   │   │   └── utils/                # Utilities
│   │   ├── modules/                   # Feature modules
│   │   │   ├── user-management/
│   │   │   ├── file-management/
│   │   │   └── workflow/
│   │   ├── components/                # Shared components
│   │   ├── layouts/                   # Layout components
│   │   ├── pages/                     # Page components
│   │   ├── stores/                    # State management
│   │   └── types/                     # TypeScript types
│   ├── public/
│   ├── package.json
│   └── tsconfig.json
└── docs/                              # Documentation
    ├── api/
    ├── architecture/
    └── user-guide/
```

### Module Definition System

```python
# core/module/base.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseModule(ABC):
    """Base class for all modules"""

    def __init__(self, app):
        self.app = app
        self.name = self.get_name()
        self.version = self.get_version()
        self.dependencies = self.get_dependencies()

    @abstractmethod
    def get_name(self) -> str:
        """Return module name"""
        pass

    @abstractmethod
    def get_version(self) -> str:
        """Return module version"""
        pass

    def get_dependencies(self) -> List[str]:
        """Return list of module dependencies"""
        return []

    def get_document_types(self) -> List[str]:
        """Return list of document types provided by this module"""
        return []

    def get_api_routes(self) -> List[Any]:
        """Return API routes for this module"""
        return []

    def get_permissions(self) -> List[Dict[str, Any]]:
        """Return default permissions for this module"""
        return []

    def install(self) -> None:
        """Install module (create tables, default data, etc.)"""
        self.create_document_types()
        self.create_default_permissions()
        self.create_default_data()

    def uninstall(self) -> None:
        """Uninstall module"""
        self.remove_document_types()
        self.remove_permissions()

    def create_document_types(self) -> None:
        """Create document types for this module"""
        for doctype in self.get_document_types():
            self.app.document_registry.register_from_schema(doctype)

    def create_default_permissions(self) -> None:
        """Create default permissions"""
        for perm in self.get_permissions():
            self.app.permission_engine.add_permission(**perm)

    def create_default_data(self) -> None:
        """Create default data (roles, users, etc.)"""
        pass

# modules/user_management/__init__.py
from core.module.base import BaseModule

class UserManagementModule(BaseModule):
    def get_name(self) -> str:
        return "user_management"

    def get_version(self) -> str:
        return "1.0.0"

    def get_document_types(self) -> List[str]:
        return ["User", "Role", "UserRole"]

    def get_permissions(self) -> List[Dict[str, Any]]:
        return [
            {
                "doctype": "User",
                "role": "System Administrator",
                "read": True,
                "write": True,
                "create": True,
                "delete": True
            },
            {
                "doctype": "User",
                "role": "User Manager",
                "read": True,
                "write": True,
                "create": True,
                "delete": False
            }
        ]

    def create_default_data(self) -> None:
        """Create default roles and admin user"""
        # Create system roles
        roles = [
            {"name": "System Administrator", "description": "Full system access"},
            {"name": "User Manager", "description": "Manage users and roles"},
            {"name": "User", "description": "Standard user access"}
        ]

        for role_data in roles:
            role = self.app.document_registry.create_document("Role", role_data)
            role.save()

        # Create admin user
        admin_user = self.app.document_registry.create_document("User", {
            "email": "admin@example.com",
            "first_name": "System",
            "last_name": "Administrator",
            "is_active": True
        })
        admin_user.save()

        # Assign admin role
        user_role = self.app.document_registry.create_document("UserRole", {
            "user": admin_user.name,
            "role": "System Administrator"
        })
        user_role.save()
```

### Module Registry and Loader

```python
# core/module/registry.py
from typing import Dict, List, Type
from .base import BaseModule

class ModuleRegistry:
    """Registry for all modules in the system"""

    def __init__(self, app):
        self.app = app
        self._modules: Dict[str, BaseModule] = {}
        self._module_classes: Dict[str, Type[BaseModule]] = {}

    def register_module(self, module_class: Type[BaseModule]) -> None:
        """Register a module class"""
        module = module_class(self.app)
        self._modules[module.name] = module
        self._module_classes[module.name] = module_class

    def get_module(self, name: str) -> BaseModule:
        """Get module by name"""
        return self._modules.get(name)

    def get_all_modules(self) -> List[BaseModule]:
        """Get all registered modules"""
        return list(self._modules.values())

    def install_module(self, name: str) -> None:
        """Install a module"""
        module = self.get_module(name)
        if not module:
            raise ValueError(f"Module {name} not found")

        # Check dependencies
        self._check_dependencies(module)

        # Install module
        module.install()

        # Mark as installed
        self._mark_installed(name)

    def uninstall_module(self, name: str) -> None:
        """Uninstall a module"""
        module = self.get_module(name)
        if not module:
            raise ValueError(f"Module {name} not found")

        # Check if other modules depend on this
        self._check_dependents(name)

        # Uninstall module
        module.uninstall()

        # Mark as uninstalled
        self._mark_uninstalled(name)

    def _check_dependencies(self, module: BaseModule) -> None:
        """Check if all dependencies are installed"""
        for dep in module.dependencies:
            if not self._is_installed(dep):
                raise ValueError(f"Dependency {dep} not installed")

    def _check_dependents(self, name: str) -> None:
        """Check if any modules depend on this module"""
        for module in self._modules.values():
            if name in module.dependencies and self._is_installed(module.name):
                raise ValueError(f"Module {module.name} depends on {name}")

    def _is_installed(self, name: str) -> bool:
        """Check if module is installed"""
        # Check in database or config
        return True  # Simplified

    def _mark_installed(self, name: str) -> None:
        """Mark module as installed"""
        # Update database or config
        pass

    def _mark_uninstalled(self, name: str) -> None:
        """Mark module as uninstalled"""
        # Update database or config
        pass
```

This modular organization provides:
- **Clear Separation**: Each module is self-contained
- **Dependency Management**: Automatic dependency resolution
- **Easy Installation**: Modules can be installed/uninstalled
- **Extensibility**: New modules can be added easily
- **Maintainability**: Code is organized by business domain

## Implementation Examples

### Python Backend Implementation

#### Main Application Setup

```python
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.database.connection import DatabaseManager
from core.cache.redis import RedisCache
from core.document.registry import DocumentRegistry
from core.permissions.engine import PermissionEngine
from core.api.router import APIRouter
from core.auth.middleware import AuthMiddleware
from core.module.registry import ModuleRegistry
from modules.user_management import UserManagementModule
from modules.file_management import FileManagementModule

class FrameworkApp:
    def __init__(self):
        self.app = FastAPI(
            title="Custom Framework",
            description="Frappe-inspired framework",
            version="1.0.0"
        )

        # Initialize core components
        self.db = DatabaseManager()
        self.cache = RedisCache()
        self.document_registry = DocumentRegistry(self.db)
        self.permission_engine = PermissionEngine(self.db, self.cache)
        self.module_registry = ModuleRegistry(self)

        # Setup middleware
        self._setup_middleware()

        # Register modules
        self._register_modules()

        # Setup API routes
        self._setup_routes()

    def _setup_middleware(self):
        """Setup middleware"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        self.app.add_middleware(AuthMiddleware)

    def _register_modules(self):
        """Register all modules"""
        self.module_registry.register_module(UserManagementModule)
        self.module_registry.register_module(FileManagementModule)

        # Install modules if not already installed
        for module in self.module_registry.get_all_modules():
            if not self.module_registry._is_installed(module.name):
                self.module_registry.install_module(module.name)

    def _setup_routes(self):
        """Setup API routes"""
        api_router = APIRouter(
            self.document_registry,
            self.permission_engine
        )

        # Include auto-generated CRUD routes
        self.app.include_router(api_router.get_crud_router(), prefix="/api")

        # Include module-specific routes
        for module in self.module_registry.get_all_modules():
            for route in module.get_api_routes():
                self.app.include_router(route, prefix="/api")

# Create application instance
framework_app = FrameworkApp()
app = framework_app.app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

#### User Document Implementation

```python
# modules/user_management/models/user.py
from core.document.base import BaseDocument
from core.permissions.decorators import requires_permission
from core.auth.utils import hash_password, verify_password
from typing import Optional
import re

class User(BaseDocument):
    @classmethod
    def get_meta(cls):
        return cls._load_meta_from_file("user.json")

    def validate_email(self):
        """Validate email format"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, self.email):
            raise ValidationError("Invalid email format")

        # Check for duplicate email
        existing = self.db.query(
            "SELECT name FROM user WHERE email = %s AND name != %s",
            [self.email, self.name or ""]
        )
        if existing:
            raise ValidationError("Email already exists")

    def set_full_name(self):
        """Set full name from first and last name"""
        parts = [self.first_name, self.last_name]
        self.full_name = " ".join(filter(None, parts))

    def set_password(self, password: str):
        """Set user password"""
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters")

        self.password_hash = hash_password(password)

    def check_password(self, password: str) -> bool:
        """Check if password is correct"""
        return verify_password(password, self.password_hash)

    @requires_permission("User", "write")
    def reset_password(self, new_password: str):
        """Reset user password"""
        self.set_password(new_password)
        self.password_reset_required = False
        self.save()

        # Send password reset notification
        self.send_password_reset_notification()

    @requires_permission("User", "write")
    def activate(self):
        """Activate user account"""
        self.is_active = True
        self.save()

    @requires_permission("User", "write")
    def deactivate(self):
        """Deactivate user account"""
        self.is_active = False
        self.save()

        # Clear active sessions
        self.clear_sessions()

    def get_roles(self) -> list:
        """Get user roles"""
        return self.db.query(
            "SELECT role FROM user_role WHERE user = %s",
            [self.name]
        )

    def add_role(self, role: str):
        """Add role to user"""
        user_role = self.document_registry.create_document("UserRole", {
            "user": self.name,
            "role": role
        })
        user_role.save()

    def remove_role(self, role: str):
        """Remove role from user"""
        self.db.execute(
            "DELETE FROM user_role WHERE user = %s AND role = %s",
            [self.name, role]
        )

    def send_welcome_email(self):
        """Send welcome email to new user"""
        from core.email.service import EmailService

        email_service = EmailService()
        email_service.send_template_email(
            template="welcome_email",
            recipients=[self.email],
            context={"user": self}
        )

    def send_password_reset_notification(self):
        """Send password reset notification"""
        from core.email.service import EmailService

        email_service = EmailService()
        email_service.send_template_email(
            template="password_reset",
            recipients=[self.email],
            context={"user": self}
        )

    def clear_sessions(self):
        """Clear all active sessions for this user"""
        from core.auth.session import SessionManager

        session_manager = SessionManager()
        session_manager.clear_user_sessions(self.name)
```

#### Go Backend Alternative

```go
// main.go
package main

import (
    "log"
    "net/http"

    "github.com/gin-gonic/gin"
    "github.com/your-org/framework/core/database"
    "github.com/your-org/framework/core/document"
    "github.com/your-org/framework/core/permissions"
    "github.com/your-org/framework/core/api"
    "github.com/your-org/framework/modules/user"
)

type FrameworkApp struct {
    Router           *gin.Engine
    DB              *database.Manager
    DocumentRegistry *document.Registry
    PermissionEngine *permissions.Engine
}

func NewFrameworkApp() *FrameworkApp {
    app := &FrameworkApp{
        Router: gin.Default(),
        DB:     database.NewManager(),
        DocumentRegistry: document.NewRegistry(),
        PermissionEngine: permissions.NewEngine(),
    }

    app.setupMiddleware()
    app.registerModules()
    app.setupRoutes()

    return app
}

func (app *FrameworkApp) setupMiddleware() {
    app.Router.Use(gin.Logger())
    app.Router.Use(gin.Recovery())
    app.Router.Use(corsMiddleware())
    app.Router.Use(authMiddleware(app.PermissionEngine))
}

func (app *FrameworkApp) registerModules() {
    // Register user management module
    userModule := user.NewModule(app.DB, app.DocumentRegistry)
    userModule.Install()
}

func (app *FrameworkApp) setupRoutes() {
    apiRouter := api.NewRouter(app.DocumentRegistry, app.PermissionEngine)

    v1 := app.Router.Group("/api/v1")
    {
        // Auto-generated CRUD routes
        apiRouter.RegisterCRUDRoutes(v1)

        // Custom routes
        v1.POST("/auth/login", apiRouter.Login)
        v1.POST("/auth/logout", apiRouter.Logout)
        v1.GET("/auth/me", apiRouter.GetCurrentUser)
    }
}

func main() {
    app := NewFrameworkApp()

    log.Println("Starting server on :8000")
    log.Fatal(http.ListenAndServe(":8000", app.Router))
}

// User document in Go
package user

import (
    "errors"
    "regexp"
    "time"

    "github.com/your-org/framework/core/document"
    "github.com/your-org/framework/core/validation"
)

type User struct {
    document.BaseDocument
    Email       string    `json:"email" db:"email"`
    FirstName   string    `json:"first_name" db:"first_name"`
    LastName    string    `json:"last_name" db:"last_name"`
    FullName    string    `json:"full_name" db:"full_name"`
    IsActive    bool      `json:"is_active" db:"is_active"`
    LastLogin   *time.Time `json:"last_login" db:"last_login"`
    PasswordHash string   `json:"-" db:"password_hash"`
}

func (u *User) GetDocType() string {
    return "User"
}

func (u *User) Validate() error {
    if err := u.validateEmail(); err != nil {
        return err
    }

    u.setFullName()
    return nil
}

func (u *User) validateEmail() error {
    emailRegex := regexp.MustCompile(`^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`)
    if !emailRegex.MatchString(u.Email) {
        return errors.New("invalid email format")
    }

    // Check for duplicate email
    var count int
    err := u.DB.QueryRow(
        "SELECT COUNT(*) FROM user WHERE email = ? AND name != ?",
        u.Email, u.Name,
    ).Scan(&count)

    if err != nil {
        return err
    }

    if count > 0 {
        return errors.New("email already exists")
    }

    return nil
}

func (u *User) setFullName() {
    if u.LastName != "" {
        u.FullName = u.FirstName + " " + u.LastName
    } else {
        u.FullName = u.FirstName
    }
}

func (u *User) SetPassword(password string) error {
    if len(password) < 8 {
        return errors.New("password must be at least 8 characters")
    }

    hash, err := hashPassword(password)
    if err != nil {
        return err
    }

    u.PasswordHash = hash
    return nil
}

func (u *User) CheckPassword(password string) bool {
    return checkPasswordHash(password, u.PasswordHash)
}
```

### TypeScript Frontend Implementation

#### API Client

```typescript
// src/core/api/client.ts
import axios, { AxiosInstance, AxiosResponse } from 'axios';

export interface APIResponse<T = any> {
  data: T;
  message?: string;
  errors?: string[];
}

export interface ListResponse<T = any> {
  data: T[];
  total_count: number;
  page: number;
  page_size: number;
  has_next: boolean;
}

export interface DocumentMeta {
  name: string;
  fields: FieldDefinition[];
  permissions: Permission[];
}

class APIClient {
  private client: AxiosInstance;
  private token: string | null = null;

  constructor(baseURL: string) {
    this.client = axios.create({
      baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor to add auth token
    this.client.interceptors.request.use((config) => {
      if (this.token) {
        config.headers.Authorization = `Bearer ${this.token}`;
      }
      return config;
    });

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          this.clearToken();
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  setToken(token: string) {
    this.token = token;
    localStorage.setItem('auth_token', token);
  }

  clearToken() {
    this.token = null;
    localStorage.removeItem('auth_token');
  }

  // Authentication
  async login(email: string, password: string): Promise<{ token: string; user: any }> {
    const response = await this.client.post('/auth/login', { email, password });
    return response.data;
  }

  async logout(): Promise<void> {
    await this.client.post('/auth/logout');
    this.clearToken();
  }

  async getCurrentUser(): Promise<any> {
    const response = await this.client.get('/auth/me');
    return response.data;
  }

  // Document operations
  async getDocumentList<T = any>(
    doctype: string,
    options: {
      page?: number;
      page_size?: number;
      fields?: string[];
      filters?: Record<string, any>;
      order_by?: string;
    } = {}
  ): Promise<ListResponse<T>> {
    const params = new URLSearchParams();

    if (options.page) params.append('page', options.page.toString());
    if (options.page_size) params.append('page_size', options.page_size.toString());
    if (options.fields) params.append('fields', JSON.stringify(options.fields));
    if (options.filters) params.append('filters', JSON.stringify(options.filters));
    if (options.order_by) params.append('order_by', options.order_by);

    const response = await this.client.get(`/doctype/${doctype}?${params}`);
    return response.data;
  }

  async getDocument<T = any>(doctype: string, name: string): Promise<T> {
    const response = await this.client.get(`/doctype/${doctype}/${name}`);
    return response.data.data;
  }

  async createDocument<T = any>(doctype: string, data: Partial<T>): Promise<T> {
    const response = await this.client.post(`/doctype/${doctype}`, data);
    return response.data.data;
  }

  async updateDocument<T = any>(
    doctype: string,
    name: string,
    data: Partial<T>
  ): Promise<T> {
    const response = await this.client.put(`/doctype/${doctype}/${name}`, data);
    return response.data.data;
  }

  async deleteDocument(doctype: string, name: string): Promise<void> {
    await this.client.delete(`/doctype/${doctype}/${name}`);
  }

  async executeDocumentMethod(
    doctype: string,
    name: string,
    method: string,
    args: Record<string, any> = {}
  ): Promise<any> {
    const response = await this.client.post(
      `/doctype/${doctype}/${name}/method/${method}`,
      args
    );
    return response.data;
  }

  // Metadata
  async getDocumentMeta(doctype: string): Promise<DocumentMeta> {
    const response = await this.client.get(`/meta/${doctype}`);
    return response.data;
  }
}

export const apiClient = new APIClient(process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1');
```

#### Form Generation System

```typescript
// src/core/forms/FormGenerator.tsx
import React from 'react';
import { useForm, Controller } from 'react-hook-form';
import { DocumentMeta, FieldDefinition } from '../types';

interface FormGeneratorProps {
  meta: DocumentMeta;
  data?: Record<string, any>;
  onSubmit: (data: Record<string, any>) => void;
  onCancel?: () => void;
  readOnly?: boolean;
}

export const FormGenerator: React.FC<FormGeneratorProps> = ({
  meta,
  data = {},
  onSubmit,
  onCancel,
  readOnly = false,
}) => {
  const { control, handleSubmit, formState: { errors } } = useForm({
    defaultValues: data,
  });

  const renderField = (field: FieldDefinition) => {
    const commonProps = {
      name: field.fieldname,
      control,
      rules: {
        required: field.required ? `${field.label} is required` : false,
      },
    };

    switch (field.fieldtype) {
      case 'Data':
      case 'Email':
      case 'Phone':
        return (
          <Controller
            {...commonProps}
            render={({ field: formField, fieldState }) => (
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {field.label}
                  {field.required && <span className="text-red-500">*</span>}
                </label>
                <input
                  {...formField}
                  type={field.fieldtype === 'Email' ? 'email' : 'text'}
                  className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                    fieldState.error ? 'border-red-500' : 'border-gray-300'
                  }`}
                  readOnly={readOnly || field.read_only}
                  maxLength={field.max_length}
                />
                {fieldState.error && (
                  <p className="mt-1 text-sm text-red-500">{fieldState.error.message}</p>
                )}
                {field.description && (
                  <p className="mt-1 text-sm text-gray-500">{field.description}</p>
                )}
              </div>
            )}
          />
        );

      case 'Text':
      case 'LongText':
        return (
          <Controller
            {...commonProps}
            render={({ field: formField, fieldState }) => (
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {field.label}
                  {field.required && <span className="text-red-500">*</span>}
                </label>
                <textarea
                  {...formField}
                  rows={field.fieldtype === 'LongText' ? 6 : 3}
                  className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                    fieldState.error ? 'border-red-500' : 'border-gray-300'
                  }`}
                  readOnly={readOnly || field.read_only}
                />
                {fieldState.error && (
                  <p className="mt-1 text-sm text-red-500">{fieldState.error.message}</p>
                )}
              </div>
            )}
          />
        );

      case 'Select':
        return (
          <Controller
            {...commonProps}
            render={({ field: formField, fieldState }) => (
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {field.label}
                  {field.required && <span className="text-red-500">*</span>}
                </label>
                <select
                  {...formField}
                  className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                    fieldState.error ? 'border-red-500' : 'border-gray-300'
                  }`}
                  disabled={readOnly || field.read_only}
                >
                  <option value="">Select {field.label}</option>
                  {field.options?.split('\n').map((option) => (
                    <option key={option} value={option}>
                      {option}
                    </option>
                  ))}
                </select>
                {fieldState.error && (
                  <p className="mt-1 text-sm text-red-500">{fieldState.error.message}</p>
                )}
              </div>
            )}
          />
        );

      case 'Check':
        return (
          <Controller
            {...commonProps}
            render={({ field: formField }) => (
              <div className="mb-4">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    {...formField}
                    checked={formField.value || false}
                    className="mr-2 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    disabled={readOnly || field.read_only}
                  />
                  <span className="text-sm font-medium text-gray-700">
                    {field.label}
                  </span>
                </label>
              </div>
            )}
          />
        );

      case 'Date':
        return (
          <Controller
            {...commonProps}
            render={({ field: formField, fieldState }) => (
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {field.label}
                  {field.required && <span className="text-red-500">*</span>}
                </label>
                <input
                  {...formField}
                  type="date"
                  className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                    fieldState.error ? 'border-red-500' : 'border-gray-300'
                  }`}
                  readOnly={readOnly || field.read_only}
                />
                {fieldState.error && (
                  <p className="mt-1 text-sm text-red-500">{fieldState.error.message}</p>
                )}
              </div>
            )}
          />
        );

      default:
        return null;
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {meta.fields
          .filter(field => !field.hidden)
          .map((field) => (
            <div key={field.fieldname} className={field.fieldtype === 'LongText' ? 'md:col-span-2' : ''}>
              {renderField(field)}
            </div>
          ))}
      </div>

      {!readOnly && (
        <div className="flex justify-end space-x-4 pt-4 border-t">
          {onCancel && (
            <button
              type="button"
              onClick={onCancel}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500"
            >
              Cancel
            </button>
          )}
          <button
            type="submit"
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            Save
          </button>
        </div>
      )}
    </form>
  );
};
```

#### Permission Hook

```typescript
// src/core/permissions/usePermissions.ts
import { useState, useEffect } from 'react';
import { apiClient } from '../api/client';

export interface UserPermissions {
  [doctype: string]: {
    read: boolean;
    write: boolean;
    create: boolean;
    delete: boolean;
    report: boolean;
    export: boolean;
    import: boolean;
    share: boolean;
    print: boolean;
    email: boolean;
  };
}

export const usePermissions = () => {
  const [permissions, setPermissions] = useState<UserPermissions>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadPermissions();
  }, []);

  const loadPermissions = async () => {
    try {
      const response = await apiClient.getCurrentUser();
      setPermissions(response.permissions || {});
    } catch (error) {
      console.error('Failed to load permissions:', error);
    } finally {
      setLoading(false);
    }
  };

  const hasPermission = (
    doctype: string,
    permission: keyof UserPermissions[string]
  ): boolean => {
    return permissions[doctype]?.[permission] || false;
  };

  const canRead = (doctype: string) => hasPermission(doctype, 'read');
  const canWrite = (doctype: string) => hasPermission(doctype, 'write');
  const canCreate = (doctype: string) => hasPermission(doctype, 'create');
  const canDelete = (doctype: string) => hasPermission(doctype, 'delete');

  return {
    permissions,
    loading,
    hasPermission,
    canRead,
    canWrite,
    canCreate,
    canDelete,
    reload: loadPermissions,
  };
};

// Permission wrapper component
export const PermissionWrapper: React.FC<{
  doctype: string;
  permission: keyof UserPermissions[string];
  children: React.ReactNode;
  fallback?: React.ReactNode;
}> = ({ doctype, permission, children, fallback = null }) => {
  const { hasPermission, loading } = usePermissions();

  if (loading) {
    return <div>Loading...</div>;
  }

  if (!hasPermission(doctype, permission)) {
    return <>{fallback}</>;
  }

  return <>{children}</>;
};
```

## Summary and Implementation Roadmap

This custom framework architecture provides a comprehensive foundation for building Frappe-inspired applications with modern technology stacks. Here's your implementation roadmap:

### Phase 1: Core Foundation (Weeks 1-4)
1. **Database Layer**
   - Set up PostgreSQL with connection pooling
   - Implement migration system
   - Create query builder abstraction

2. **Document Engine**
   - Implement BaseDocument class
   - Create document registry and factory
   - Build validation framework
   - Add lifecycle hooks system

3. **Basic API Framework**
   - Set up FastAPI/Gin with middleware
   - Implement auto-generated CRUD endpoints
   - Add request/response validation
   - Create error handling system

### Phase 2: Security & Permissions (Weeks 5-8)
1. **Authentication System**
   - JWT token management
   - Session handling
   - Password hashing and validation
   - Multi-factor authentication support

2. **Permission Engine**
   - Role-based access control
   - Document-level permissions
   - Field-level permissions
   - User permissions and sharing

3. **API Security**
   - Permission middleware
   - Rate limiting
   - Input sanitization
   - CORS configuration

### Phase 3: Advanced Features (Weeks 9-12)
1. **Background Processing**
   - Job queue system (Celery/Asynq)
   - Scheduler for recurring tasks
   - Event system and hooks
   - Email notifications

2. **File Management**
   - File upload/download
   - Image processing
   - Storage backends (local/cloud)
   - Attachment system

3. **Frontend Framework**
   - TypeScript API client
   - Form generation system
   - Permission-aware components
   - Real-time updates (WebSocket)

### Phase 4: Business Features (Weeks 13-16)
1. **Workflow Engine**
   - State management
   - Approval processes
   - Conditional logic
   - Notifications

2. **Reporting System**
   - Query builder UI
   - Report generation
   - Export capabilities
   - Dashboard widgets

3. **Module System**
   - Plugin architecture
   - Module installation/removal
   - Dependency management
   - Configuration system

### Technology Recommendations

#### Backend Choice
- **Python + FastAPI**: Faster development, rich ecosystem, easier for complex business logic
- **Go + Gin**: Better performance, simpler deployment, good for high-throughput APIs

#### Frontend Choice
- **React + TypeScript**: Large ecosystem, mature tooling, good for complex UIs
- **Vue.js + TypeScript**: Simpler learning curve, good performance, progressive adoption

#### Database & Infrastructure
- **PostgreSQL**: Rich feature set, JSON support, excellent for complex queries
- **Redis**: Caching and session storage
- **Docker**: Containerization for easy deployment
- **Nginx**: Reverse proxy and static file serving

### Key Advantages Over Frappe

1. **Modern Technology Stack**: Latest versions of frameworks and libraries
2. **Type Safety**: Full TypeScript support for better development experience
3. **Performance**: Optimized for modern deployment patterns
4. **Flexibility**: Not tied to specific UI framework or deployment method
5. **Closed Source**: Full control over intellectual property
6. **Cloud Native**: Designed for containerized deployments
7. **API First**: Built with API-first approach for better integration

### Getting Started

1. **Choose Your Stack**: Decide between Python/Go for backend
2. **Set Up Development Environment**: Docker, database, IDE
3. **Start with Core**: Implement document engine and basic API
4. **Add Authentication**: User management and permissions
5. **Build Frontend**: Create admin interface and forms
6. **Iterate**: Add features based on business requirements

This architecture gives you the power and flexibility of Frappe while maintaining full control over your codebase and technology choices. The modular design allows you to implement features incrementally and adapt the system to your specific needs.
