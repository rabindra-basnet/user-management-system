from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.api import deps
from app.models.user import User, Role
from app.schemas.user import (
    Role as RoleSchema, RoleCreate, RoleUpdate
)
from app.services.permission_service import PermissionService
import uuid

router = APIRouter()


@router.get("/", response_model=List[RoleSchema])
def read_roles(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(deps.require_permission("roles.read"))
) -> Any:
    """Get all roles with pagination"""
    
    permission_service = PermissionService(db)
    roles = permission_service.get_roles(skip=skip, limit=limit)
    return roles


@router.post("/", response_model=RoleSchema)
def create_role(
    *,
    db: Session = Depends(deps.get_db),
    role_in: RoleCreate,
    current_user: User = Depends(deps.require_permission("roles.create"))
) -> Any:
    """Create new role"""
    
    permission_service = PermissionService(db)
    role = permission_service.create_role(role_in)
    return role


@router.get("/{role_id}", response_model=RoleSchema)
def read_role(
    *,
    db: Session = Depends(deps.get_db),
    role_id: uuid.UUID,
    current_user: User = Depends(deps.require_permission("roles.read"))
) -> Any:
    """Get role by ID"""
    
    permission_service = PermissionService(db)
    role = permission_service.get_role_by_id(role_id)
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    return role


@router.put("/{role_id}", response_model=RoleSchema)
def update_role(
    *,
    db: Session = Depends(deps.get_db),
    role_id: uuid.UUID,
    role_in: RoleUpdate,
    current_user: User = Depends(deps.require_permission("roles.update"))
) -> Any:
    """Update role"""
    
    permission_service = PermissionService(db)
    role = permission_service.update_role(role_id, role_in)
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    return role


@router.delete("/{role_id}")
def delete_role(
    *,
    db: Session = Depends(deps.get_db),
    role_id: uuid.UUID,
    current_user: User = Depends(deps.require_permission("roles.delete"))
) -> Any:
    """Delete role"""
    
    permission_service = PermissionService(db)
    success = permission_service.delete_role(role_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    return {"message": "Role deleted successfully"}


@router.get("/{role_id}/users", response_model=List[dict])
def get_role_users(
    *,
    db: Session = Depends(deps.get_db),
    role_id: uuid.UUID,
    current_user: User = Depends(deps.require_permission("roles.read"))
) -> Any:
    """Get users assigned to a role"""
    
    permission_service = PermissionService(db)
    role = permission_service.get_role_by_id(role_id)
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    users = [
        {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_active": user.is_active
        }
        for user in role.users
    ]
    
    return users
