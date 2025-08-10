from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from fastapi import HTTPException, status
from app.models.user import User, UserSession, APIKey, AuditLog
from app.schemas.user import UserCreate, UserUpdate, APIKeyCreate, APIKeyResponse
from app.core.security import get_password_hash, generate_api_key, hash_api_key, validate_password_strength
from datetime import datetime
import uuid
import json


class UserService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_users(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        search: str = None, 
        is_active: bool = None
    ) -> Tuple[List[User], int]:
        """Get users with pagination and filtering"""
        
        query = self.db.query(User)
        
        # Apply filters
        if search:
            search_filter = or_(
                User.email.ilike(f"%{search}%"),
                User.first_name.ilike(f"%{search}%"),
                User.last_name.ilike(f"%{search}%"),
                User.username.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        users = query.offset(skip).limit(limit).all()
        
        return users, total
    
    def get_user_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.db.query(User).filter(User.username == username).first()
    
    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user"""
        
        # Check if user already exists
        existing_user = self.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        if user_data.username:
            existing_username = self.get_user_by_username(user_data.username)
            if existing_username:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User with this username already exists"
                )
        
        # Validate password strength
        is_valid, errors = validate_password_strength(user_data.password)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": "Password does not meet security requirements", "errors": errors}
            )
        
        # Create user
        user = User(
            email=user_data.email,
            username=user_data.username,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            phone_number=user_data.phone_number,
            bio=user_data.bio,
            timezone=user_data.timezone,
            language=user_data.language,
            hashed_password=get_password_hash(user_data.password),
            is_active=user_data.is_active
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def update_user(self, user_id: uuid.UUID, user_data: UserUpdate) -> Optional[User]:
        """Update user"""
        
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        # Check for email conflicts
        if user_data.email and user_data.email != user.email:
            existing_user = self.get_user_by_email(user_data.email)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User with this email already exists"
                )
        
        # Check for username conflicts
        if user_data.username and user_data.username != user.username:
            existing_username = self.get_user_by_username(user_data.username)
            if existing_username:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User with this username already exists"
                )
        
        # Update fields
        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def delete_user(self, user_id: uuid.UUID) -> bool:
        """Delete user"""
        
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        # Check if user is superuser
        if user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot delete superuser"
            )
        
        self.db.delete(user)
        self.db.commit()
        
        return True
    
    def activate_user(self, user_id: uuid.UUID) -> bool:
        """Activate user account"""
        
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        user.is_active = True
        self.db.commit()
        
        return True
    
    def deactivate_user(self, user_id: uuid.UUID) -> bool:
        """Deactivate user account"""
        
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        # Check if user is superuser
        if user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot deactivate superuser"
            )
        
        user.is_active = False
        
        # Invalidate all user sessions
        self.db.query(UserSession).filter(
            UserSession.user_id == user_id,
            UserSession.is_active == True
        ).update({"is_active": False})
        
        self.db.commit()
        
        return True
    
    def get_user_sessions(self, user_id: uuid.UUID) -> List[UserSession]:
        """Get user sessions"""
        
        return self.db.query(UserSession).filter(
            UserSession.user_id == user_id
        ).order_by(UserSession.created_at.desc()).all()
    
    def revoke_session(self, session_id: uuid.UUID) -> bool:
        """Revoke user session"""
        
        session = self.db.query(UserSession).filter(UserSession.id == session_id).first()
        if not session:
            return False
        
        session.is_active = False
        self.db.commit()
        
        return True
    
    def create_api_key(self, user_id: uuid.UUID, api_key_data: APIKeyCreate) -> Optional[APIKeyResponse]:
        """Create API key for user"""
        
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        # Generate API key
        api_key = generate_api_key()
        api_key_hash = hash_api_key(api_key)
        
        # Create API key record
        api_key_record = APIKey(
            user_id=user_id,
            name=api_key_data.name,
            key_hash=api_key_hash,
            scopes=json.dumps(api_key_data.scopes) if api_key_data.scopes else None,
            expires_at=api_key_data.expires_at
        )
        
        self.db.add(api_key_record)
        self.db.commit()
        self.db.refresh(api_key_record)
        
        # Return API key with full key (only shown once)
        return APIKeyResponse(
            api_key=api_key_record,
            key=api_key
        )
    
    def get_user_api_keys(self, user_id: uuid.UUID) -> List[APIKey]:
        """Get user API keys"""
        
        return self.db.query(APIKey).filter(
            APIKey.user_id == user_id
        ).order_by(APIKey.created_at.desc()).all()
    
    def revoke_api_key(self, api_key_id: uuid.UUID) -> bool:
        """Revoke API key"""
        
        api_key = self.db.query(APIKey).filter(APIKey.id == api_key_id).first()
        if not api_key:
            return False
        
        api_key.is_active = False
        self.db.commit()
        
        return True
    
    def get_user_audit_logs(self, user_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[AuditLog]:
        """Get user audit logs"""
        
        return self.db.query(AuditLog).filter(
            AuditLog.user_id == user_id
        ).order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
    
    def search_users(self, query: str, limit: int = 10) -> List[User]:
        """Search users by name or email"""
        
        search_filter = or_(
            User.email.ilike(f"%{query}%"),
            User.first_name.ilike(f"%{query}%"),
            User.last_name.ilike(f"%{query}%"),
            User.username.ilike(f"%{query}%")
        )
        
        return self.db.query(User).filter(
            and_(User.is_active == True, search_filter)
        ).limit(limit).all()
    
    def get_user_statistics(self) -> dict:
        """Get user statistics"""
        
        total_users = self.db.query(User).count()
        active_users = self.db.query(User).filter(User.is_active == True).count()
        verified_users = self.db.query(User).filter(User.is_verified == True).count()
        users_with_2fa = self.db.query(User).filter(User.is_2fa_enabled == True).count()
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "inactive_users": total_users - active_users,
            "verified_users": verified_users,
            "unverified_users": total_users - verified_users,
            "users_with_2fa": users_with_2fa,
            "users_without_2fa": total_users - users_with_2fa
        }
