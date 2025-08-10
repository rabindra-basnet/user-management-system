from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User, Role, Permission
from app.schemas.user import RoleCreate, RoleUpdate, PermissionCreate
import uuid


class PermissionService:
    def __init__(self, db: Session):
        self.db = db
    
    # Permission Management
    def create_permission(self, permission_data: PermissionCreate) -> Permission:
        """Create a new permission"""
        
        # Check if permission already exists
        existing = self.db.query(Permission).filter(
            Permission.name == permission_data.name
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Permission with this name already exists"
            )
        
        permission = Permission(
            name=permission_data.name,
            description=permission_data.description,
            resource=permission_data.resource,
            action=permission_data.action
        )
        
        self.db.add(permission)
        self.db.commit()
        self.db.refresh(permission)
        
        return permission
    
    def get_permissions(self, skip: int = 0, limit: int = 100) -> List[Permission]:
        """Get all permissions with pagination"""
        return self.db.query(Permission).offset(skip).limit(limit).all()
    
    def get_permission_by_id(self, permission_id: uuid.UUID) -> Optional[Permission]:
        """Get permission by ID"""
        return self.db.query(Permission).filter(Permission.id == permission_id).first()
    
    def get_permission_by_name(self, name: str) -> Optional[Permission]:
        """Get permission by name"""
        return self.db.query(Permission).filter(Permission.name == name).first()
    
    def delete_permission(self, permission_id: uuid.UUID) -> bool:
        """Delete a permission"""
        permission = self.get_permission_by_id(permission_id)
        if not permission:
            return False
        
        self.db.delete(permission)
        self.db.commit()
        return True
    
    # Role Management
    def create_role(self, role_data: RoleCreate) -> Role:
        """Create a new role with permissions"""
        
        # Check if role already exists
        existing = self.db.query(Role).filter(Role.name == role_data.name).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role with this name already exists"
            )
        
        # Create role
        role = Role(
            name=role_data.name,
            description=role_data.description
        )
        
        # Add permissions if provided
        if role_data.permission_ids:
            permissions = self.db.query(Permission).filter(
                Permission.id.in_(role_data.permission_ids)
            ).all()
            
            if len(permissions) != len(role_data.permission_ids):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="One or more permission IDs are invalid"
                )
            
            role.permissions = permissions
        
        self.db.add(role)
        self.db.commit()
        self.db.refresh(role)
        
        return role
    
    def get_roles(self, skip: int = 0, limit: int = 100) -> List[Role]:
        """Get all roles with pagination"""
        return self.db.query(Role).offset(skip).limit(limit).all()
    
    def get_role_by_id(self, role_id: uuid.UUID) -> Optional[Role]:
        """Get role by ID"""
        return self.db.query(Role).filter(Role.id == role_id).first()
    
    def get_role_by_name(self, name: str) -> Optional[Role]:
        """Get role by name"""
        return self.db.query(Role).filter(Role.name == name).first()
    
    def update_role(self, role_id: uuid.UUID, role_data: RoleUpdate) -> Optional[Role]:
        """Update a role"""
        role = self.get_role_by_id(role_id)
        if not role:
            return None
        
        # Check if role is system role
        if role.is_system_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot modify system role"
            )
        
        # Update basic fields
        if role_data.name is not None:
            # Check for name conflicts
            existing = self.db.query(Role).filter(
                Role.name == role_data.name,
                Role.id != role_id
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Role with this name already exists"
                )
            role.name = role_data.name
        
        if role_data.description is not None:
            role.description = role_data.description
        
        # Update permissions
        if role_data.permission_ids is not None:
            permissions = self.db.query(Permission).filter(
                Permission.id.in_(role_data.permission_ids)
            ).all()
            
            if len(permissions) != len(role_data.permission_ids):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="One or more permission IDs are invalid"
                )
            
            role.permissions = permissions
        
        self.db.commit()
        self.db.refresh(role)
        
        return role
    
    def delete_role(self, role_id: uuid.UUID) -> bool:
        """Delete a role"""
        role = self.get_role_by_id(role_id)
        if not role:
            return False
        
        # Check if role is system role
        if role.is_system_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot delete system role"
            )
        
        # Check if role is assigned to any users
        if role.users:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete role that is assigned to users"
            )
        
        self.db.delete(role)
        self.db.commit()
        return True
    
    # User Role Management
    def assign_role_to_user(self, user_id: uuid.UUID, role_id: uuid.UUID) -> bool:
        """Assign a role to a user"""
        user = self.db.query(User).filter(User.id == user_id).first()
        role = self.db.query(Role).filter(Role.id == role_id).first()
        
        if not user or not role:
            return False
        
        # Check if user already has this role
        if role in user.roles:
            return True
        
        user.roles.append(role)
        self.db.commit()
        return True
    
    def remove_role_from_user(self, user_id: uuid.UUID, role_id: uuid.UUID) -> bool:
        """Remove a role from a user"""
        user = self.db.query(User).filter(User.id == user_id).first()
        role = self.db.query(Role).filter(Role.id == role_id).first()
        
        if not user or not role:
            return False
        
        # Check if user has this role
        if role not in user.roles:
            return True
        
        user.roles.remove(role)
        self.db.commit()
        return True
    
    def get_user_permissions(self, user_id: uuid.UUID) -> List[Permission]:
        """Get all permissions for a user through their roles"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return []
        
        permissions = set()
        for role in user.roles:
            for permission in role.permissions:
                permissions.add(permission)
        
        return list(permissions)
    
    def check_user_permission(self, user_id: uuid.UUID, permission_name: str) -> bool:
        """Check if user has a specific permission"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        return user.has_permission(permission_name)
    
    def check_user_role(self, user_id: uuid.UUID, role_name: str) -> bool:
        """Check if user has a specific role"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        return user.has_role(role_name)
    
    # System Initialization
    def create_default_permissions(self) -> List[Permission]:
        """Create default system permissions"""
        default_permissions = [
            # User management
            {"name": "users.create", "description": "Create users", "resource": "users", "action": "create"},
            {"name": "users.read", "description": "Read users", "resource": "users", "action": "read"},
            {"name": "users.update", "description": "Update users", "resource": "users", "action": "update"},
            {"name": "users.delete", "description": "Delete users", "resource": "users", "action": "delete"},
            
            # Role management
            {"name": "roles.create", "description": "Create roles", "resource": "roles", "action": "create"},
            {"name": "roles.read", "description": "Read roles", "resource": "roles", "action": "read"},
            {"name": "roles.update", "description": "Update roles", "resource": "roles", "action": "update"},
            {"name": "roles.delete", "description": "Delete roles", "resource": "roles", "action": "delete"},
            
            # Permission management
            {"name": "permissions.create", "description": "Create permissions", "resource": "permissions", "action": "create"},
            {"name": "permissions.read", "description": "Read permissions", "resource": "permissions", "action": "read"},
            {"name": "permissions.delete", "description": "Delete permissions", "resource": "permissions", "action": "delete"},
            
            # System administration
            {"name": "system.admin", "description": "System administration", "resource": "system", "action": "admin"},
            {"name": "audit.read", "description": "Read audit logs", "resource": "audit", "action": "read"},
        ]
        
        created_permissions = []
        for perm_data in default_permissions:
            existing = self.db.query(Permission).filter(Permission.name == perm_data["name"]).first()
            if not existing:
                permission = Permission(**perm_data)
                self.db.add(permission)
                created_permissions.append(permission)
        
        self.db.commit()
        return created_permissions
    
    def create_default_roles(self) -> List[Role]:
        """Create default system roles"""
        # Ensure default permissions exist
        self.create_default_permissions()
        
        # Get all permissions
        all_permissions = self.db.query(Permission).all()
        user_permissions = [p for p in all_permissions if p.resource == "users" and p.action == "read"]
        admin_permissions = all_permissions
        
        default_roles = [
            {
                "name": "Administrator",
                "description": "Full system access",
                "permissions": admin_permissions,
                "is_system_role": True
            },
            {
                "name": "User Manager",
                "description": "Manage users and basic operations",
                "permissions": [p for p in all_permissions if p.resource in ["users", "roles"] and p.action in ["create", "read", "update"]],
                "is_system_role": True
            },
            {
                "name": "User",
                "description": "Basic user access",
                "permissions": user_permissions,
                "is_system_role": True
            }
        ]
        
        created_roles = []
        for role_data in default_roles:
            existing = self.db.query(Role).filter(Role.name == role_data["name"]).first()
            if not existing:
                role = Role(
                    name=role_data["name"],
                    description=role_data["description"],
                    is_system_role=role_data["is_system_role"]
                )
                role.permissions = role_data["permissions"]
                self.db.add(role)
                created_roles.append(role)
        
        self.db.commit()
        return created_roles
