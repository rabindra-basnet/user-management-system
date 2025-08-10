from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.api import deps
from app.models.user import User
from app.schemas.user import (
    Permission as PermissionSchema, PermissionCreate
)
from app.services.permission_service import PermissionService
import uuid

router = APIRouter()


@router.get("/", response_model=List[PermissionSchema])
def read_permissions(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(deps.require_permission("permissions.read"))
) -> Any:
    """Get all permissions with pagination"""
    
    permission_service = PermissionService(db)
    permissions = permission_service.get_permissions(skip=skip, limit=limit)
    return permissions


@router.post("/", response_model=PermissionSchema)
def create_permission(
    *,
    db: Session = Depends(deps.get_db),
    permission_in: PermissionCreate,
    current_user: User = Depends(deps.require_permission("permissions.create"))
) -> Any:
    """Create new permission"""
    
    permission_service = PermissionService(db)
    permission = permission_service.create_permission(permission_in)
    return permission


@router.get("/{permission_id}", response_model=PermissionSchema)
def read_permission(
    *,
    db: Session = Depends(deps.get_db),
    permission_id: uuid.UUID,
    current_user: User = Depends(deps.require_permission("permissions.read"))
) -> Any:
    """Get permission by ID"""
    
    permission_service = PermissionService(db)
    permission = permission_service.get_permission_by_id(permission_id)
    
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found"
        )
    
    return permission


@router.delete("/{permission_id}")
def delete_permission(
    *,
    db: Session = Depends(deps.get_db),
    permission_id: uuid.UUID,
    current_user: User = Depends(deps.require_permission("permissions.delete"))
) -> Any:
    """Delete permission"""
    
    permission_service = PermissionService(db)
    success = permission_service.delete_permission(permission_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found"
        )
    
    return {"message": "Permission deleted successfully"}


@router.post("/initialize")
def initialize_default_permissions(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_permission("system.admin"))
) -> Any:
    """Initialize default permissions and roles"""
    
    permission_service = PermissionService(db)
    
    # Create default permissions
    permissions = permission_service.create_default_permissions()
    
    # Create default roles
    roles = permission_service.create_default_roles()
    
    return {
        "message": "Default permissions and roles initialized",
        "permissions_created": len(permissions),
        "roles_created": len(roles)
    }
