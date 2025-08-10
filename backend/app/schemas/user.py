from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


# Base User Schema
class UserBase(BaseModel):
    email: EmailStr
    username: Optional[str] = None
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    phone_number: Optional[str] = None
    bio: Optional[str] = None
    timezone: str = "UTC"
    language: str = "en"
    is_active: bool = True


# User Creation Schema
class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    confirm_password: str
    
    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v


# User Update Schema
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    phone_number: Optional[str] = None
    bio: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None
    is_active: Optional[bool] = None


# Password Change Schema
class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str
    
    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v


# Password Reset Schema
class PasswordReset(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str
    
    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v


# User Response Schema
class User(UserBase):
    id: UUID
    is_verified: bool
    is_superuser: bool
    is_2fa_enabled: bool
    last_login: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    roles: List['Role'] = []
    
    class Config:
        from_attributes = True


# User List Response Schema
class UserList(BaseModel):
    users: List[User]
    total: int
    page: int
    size: int
    pages: int


# Role Schemas
class RoleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None


class RoleCreate(RoleBase):
    permission_ids: List[UUID] = []


class RoleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = None
    permission_ids: Optional[List[UUID]] = None


class Role(RoleBase):
    id: UUID
    is_system_role: bool
    created_at: datetime
    updated_at: datetime
    permissions: List['Permission'] = []
    
    class Config:
        from_attributes = True


# Permission Schemas
class PermissionBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    resource: str = Field(..., min_length=1, max_length=50)
    action: str = Field(..., min_length=1, max_length=50)


class PermissionCreate(PermissionBase):
    pass


class Permission(PermissionBase):
    id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


# Authentication Schemas
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenRefresh(BaseModel):
    refresh_token: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    remember_me: bool = False


class LoginResponse(BaseModel):
    user: User
    token: Token
    message: str = "Login successful"


# Two-Factor Authentication Schemas
class TwoFactorSetup(BaseModel):
    secret: str
    qr_code: str
    backup_codes: List[str]


class TwoFactorVerify(BaseModel):
    code: str


class TwoFactorDisable(BaseModel):
    password: str
    code: str


# API Key Schemas
class APIKeyBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    scopes: Optional[List[str]] = []
    expires_at: Optional[datetime] = None


class APIKeyCreate(APIKeyBase):
    pass


class APIKey(APIKeyBase):
    id: UUID
    key_preview: str  # Only show first 8 characters
    last_used: Optional[datetime]
    usage_count: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class APIKeyResponse(BaseModel):
    api_key: APIKey
    key: str  # Full key only returned on creation


# Session Schemas
class UserSession(BaseModel):
    id: UUID
    ip_address: Optional[str]
    user_agent: Optional[str]
    device_info: Optional[str]
    is_active: bool
    last_activity: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


# Audit Log Schemas
class AuditLog(BaseModel):
    id: UUID
    action: str
    resource: Optional[str]
    resource_id: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    endpoint: Optional[str]
    method: Optional[str]
    details: Optional[str]
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Update forward references
User.model_rebuild()
Role.model_rebuild()
