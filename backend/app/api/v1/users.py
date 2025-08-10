from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.api import deps
from app.models.user import User
from app.schemas.user import (
    User as UserSchema, UserCreate, UserUpdate, UserList,
    APIKeyCreate, APIKeyResponse, UserSession, AuditLog
)
from app.services.user_service import UserService
from app.services.permission_service import PermissionService
import uuid

router = APIRouter()


@router.get("/", response_model=UserList)
def read_users(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: str = Query(None),
    is_active: bool = Query(None),
    current_user: User = Depends(deps.require_permission("users.read"))
) -> Any:
    """Get users with pagination and filtering"""
    
    user_service = UserService(db)
    users, total = user_service.get_users(
        skip=skip,
        limit=limit,
        search=search,
        is_active=is_active
    )
    
    pages = (total + limit - 1) // limit
    
    return UserList(
        users=users,
        total=total,
        page=(skip // limit) + 1,
        size=limit,
        pages=pages
    )


@router.post("/", response_model=UserSchema)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserCreate,
    current_user: User = Depends(deps.require_permission("users.create"))
) -> Any:
    """Create new user"""
    
    user_service = UserService(db)
    user = user_service.create_user(user_in)
    return user


@router.get("/{user_id}", response_model=UserSchema)
def read_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: uuid.UUID,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """Get user by ID"""
    
    # Users can read their own profile, or need users.read permission
    if str(current_user.id) != str(user_id) and not current_user.has_permission("users.read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user_service = UserService(db)
    user = user_service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.put("/{user_id}", response_model=UserSchema)
def update_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: uuid.UUID,
    user_in: UserUpdate,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """Update user"""
    
    # Users can update their own profile, or need users.update permission
    if str(current_user.id) != str(user_id) and not current_user.has_permission("users.update"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user_service = UserService(db)
    user = user_service.update_user(user_id, user_in)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.delete("/{user_id}")
def delete_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: uuid.UUID,
    current_user: User = Depends(deps.require_permission("users.delete"))
) -> Any:
    """Delete user"""
    
    # Prevent self-deletion
    if str(current_user.id) == str(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    user_service = UserService(db)
    success = user_service.delete_user(user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"message": "User deleted successfully"}


@router.post("/{user_id}/activate")
def activate_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: uuid.UUID,
    current_user: User = Depends(deps.require_permission("users.update"))
) -> Any:
    """Activate user account"""
    
    user_service = UserService(db)
    success = user_service.activate_user(user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"message": "User activated successfully"}


@router.post("/{user_id}/deactivate")
def deactivate_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: uuid.UUID,
    current_user: User = Depends(deps.require_permission("users.update"))
) -> Any:
    """Deactivate user account"""
    
    # Prevent self-deactivation
    if str(current_user.id) == str(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account"
        )
    
    user_service = UserService(db)
    success = user_service.deactivate_user(user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"message": "User deactivated successfully"}


@router.post("/{user_id}/roles/{role_id}")
def assign_role(
    *,
    db: Session = Depends(deps.get_db),
    user_id: uuid.UUID,
    role_id: uuid.UUID,
    current_user: User = Depends(deps.require_permission("users.update"))
) -> Any:
    """Assign role to user"""
    
    permission_service = PermissionService(db)
    success = permission_service.assign_role_to_user(user_id, role_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User or role not found"
        )
    
    return {"message": "Role assigned successfully"}


@router.delete("/{user_id}/roles/{role_id}")
def remove_role(
    *,
    db: Session = Depends(deps.get_db),
    user_id: uuid.UUID,
    role_id: uuid.UUID,
    current_user: User = Depends(deps.require_permission("users.update"))
) -> Any:
    """Remove role from user"""
    
    permission_service = PermissionService(db)
    success = permission_service.remove_role_from_user(user_id, role_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User or role not found"
        )
    
    return {"message": "Role removed successfully"}


@router.get("/{user_id}/sessions", response_model=List[UserSession])
def get_user_sessions(
    *,
    db: Session = Depends(deps.get_db),
    user_id: uuid.UUID,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """Get user sessions"""
    
    # Users can view their own sessions, or need users.read permission
    if str(current_user.id) != str(user_id) and not current_user.has_permission("users.read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user_service = UserService(db)
    sessions = user_service.get_user_sessions(user_id)
    return sessions


@router.delete("/{user_id}/sessions/{session_id}")
def revoke_session(
    *,
    db: Session = Depends(deps.get_db),
    user_id: uuid.UUID,
    session_id: uuid.UUID,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """Revoke user session"""
    
    # Users can revoke their own sessions, or need users.update permission
    if str(current_user.id) != str(user_id) and not current_user.has_permission("users.update"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user_service = UserService(db)
    success = user_service.revoke_session(session_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    return {"message": "Session revoked successfully"}


@router.post("/{user_id}/api-keys", response_model=APIKeyResponse)
def create_api_key(
    *,
    db: Session = Depends(deps.get_db),
    user_id: uuid.UUID,
    api_key_in: APIKeyCreate,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """Create API key for user"""
    
    # Users can create their own API keys, or need users.update permission
    if str(current_user.id) != str(user_id) and not current_user.has_permission("users.update"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user_service = UserService(db)
    api_key_response = user_service.create_api_key(user_id, api_key_in)
    
    if not api_key_response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return api_key_response


@router.get("/{user_id}/audit-logs", response_model=List[AuditLog])
def get_user_audit_logs(
    *,
    db: Session = Depends(deps.get_db),
    user_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(deps.require_permission("audit.read"))
) -> Any:
    """Get user audit logs"""
    
    user_service = UserService(db)
    audit_logs = user_service.get_user_audit_logs(user_id, skip, limit)
    return audit_logs
