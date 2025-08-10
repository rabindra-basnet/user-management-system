from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User, UserSession, AuditLog
from app.core.security import (
    verify_password, 
    get_password_hash, 
    create_access_token, 
    create_refresh_token,
    verify_token,
    create_session_token,
    validate_password_strength
)
from app.core.config import settings
from app.schemas.user import UserCreate, LoginRequest
import pyotp
import qrcode
import io
import base64
import secrets
import json


class AuthService:
    def __init__(self, db: Session):
        self.db = db
    
    def authenticate_user(self, email: str, password: str, ip_address: str = None, user_agent: str = None) -> Optional[User]:
        """Authenticate user with email and password"""
        user = self.db.query(User).filter(User.email == email).first()
        
        if not user:
            # Log failed login attempt
            self._log_audit_event(
                action="login_failed",
                details={"reason": "user_not_found", "email": email},
                ip_address=ip_address,
                user_agent=user_agent,
                status="failure"
            )
            return None
        
        # Check if account is locked
        if user.is_locked:
            self._log_audit_event(
                user_id=user.id,
                action="login_failed",
                details={"reason": "account_locked"},
                ip_address=ip_address,
                user_agent=user_agent,
                status="failure"
            )
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail="Account is temporarily locked due to too many failed login attempts"
            )
        
        # Check if account is active
        if not user.is_active:
            self._log_audit_event(
                user_id=user.id,
                action="login_failed",
                details={"reason": "account_inactive"},
                ip_address=ip_address,
                user_agent=user_agent,
                status="failure"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive"
            )
        
        # Verify password
        if not verify_password(password, user.hashed_password):
            # Increment failed login attempts
            user.failed_login_attempts += 1
            
            # Lock account if too many failed attempts
            if user.failed_login_attempts >= settings.MAX_LOGIN_ATTEMPTS:
                user.locked_until = datetime.utcnow() + timedelta(
                    minutes=settings.ACCOUNT_LOCKOUT_DURATION_MINUTES
                )
                self._log_audit_event(
                    user_id=user.id,
                    action="account_locked",
                    details={"reason": "too_many_failed_attempts"},
                    ip_address=ip_address,
                    user_agent=user_agent,
                    status="success"
                )
            
            self.db.commit()
            
            self._log_audit_event(
                user_id=user.id,
                action="login_failed",
                details={"reason": "invalid_password"},
                ip_address=ip_address,
                user_agent=user_agent,
                status="failure"
            )
            return None
        
        # Reset failed login attempts on successful authentication
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login = datetime.utcnow()
        self.db.commit()
        
        self._log_audit_event(
            user_id=user.id,
            action="login_success",
            ip_address=ip_address,
            user_agent=user_agent,
            status="success"
        )
        
        return user
    
    def create_user_session(self, user: User, ip_address: str = None, user_agent: str = None, remember_me: bool = False) -> Tuple[str, str]:
        """Create a new user session and return access and refresh tokens"""
        
        # Create tokens
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(subject=str(user.id), expires_delta=access_token_expires)
        refresh_token = create_refresh_token(subject=str(user.id))
        
        # Create session record
        session_expires = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        if remember_me:
            session_expires = datetime.utcnow() + timedelta(days=30)  # Extended session
        
        session = UserSession(
            user_id=user.id,
            session_token=create_session_token(),
            refresh_token=refresh_token,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=session_expires
        )
        
        self.db.add(session)
        self.db.commit()
        
        return access_token, refresh_token
    
    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """Refresh access token using refresh token"""
        user_id = verify_token(refresh_token, token_type="refresh")
        if not user_id:
            return None
        
        # Verify session exists and is active
        session = self.db.query(UserSession).filter(
            UserSession.refresh_token == refresh_token,
            UserSession.is_active == True,
            UserSession.expires_at > datetime.utcnow()
        ).first()
        
        if not session:
            return None
        
        # Update session activity
        session.last_activity = datetime.utcnow()
        self.db.commit()
        
        # Create new access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(subject=user_id, expires_delta=access_token_expires)
        
        return access_token
    
    def logout_user(self, refresh_token: str, ip_address: str = None, user_agent: str = None) -> bool:
        """Logout user by invalidating session"""
        session = self.db.query(UserSession).filter(
            UserSession.refresh_token == refresh_token,
            UserSession.is_active == True
        ).first()
        
        if session:
            session.is_active = False
            self.db.commit()
            
            self._log_audit_event(
                user_id=session.user_id,
                action="logout",
                ip_address=ip_address,
                user_agent=user_agent,
                status="success"
            )
            return True
        
        return False
    
    def logout_all_sessions(self, user_id: str) -> int:
        """Logout user from all sessions"""
        sessions = self.db.query(UserSession).filter(
            UserSession.user_id == user_id,
            UserSession.is_active == True
        ).all()
        
        count = 0
        for session in sessions:
            session.is_active = False
            count += 1
        
        self.db.commit()
        
        self._log_audit_event(
            user_id=user_id,
            action="logout_all_sessions",
            details={"sessions_count": count},
            status="success"
        )
        
        return count
    
    def register_user(self, user_data: UserCreate, ip_address: str = None, user_agent: str = None) -> User:
        """Register a new user"""
        
        # Check if user already exists
        existing_user = self.db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
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
        
        self._log_audit_event(
            user_id=user.id,
            action="user_registered",
            ip_address=ip_address,
            user_agent=user_agent,
            status="success"
        )
        
        return user
    
    def change_password(self, user: User, current_password: str, new_password: str) -> bool:
        """Change user password"""
        
        # Verify current password
        if not verify_password(current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Validate new password strength
        is_valid, errors = validate_password_strength(new_password)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": "New password does not meet security requirements", "errors": errors}
            )
        
        # Update password
        user.hashed_password = get_password_hash(new_password)
        user.password_changed_at = datetime.utcnow()
        self.db.commit()
        
        # Invalidate all sessions except current one
        self.logout_all_sessions(str(user.id))
        
        self._log_audit_event(
            user_id=user.id,
            action="password_changed",
            status="success"
        )
        
        return True
    
    def _log_audit_event(self, action: str, user_id: str = None, resource: str = None, 
                        resource_id: str = None, ip_address: str = None, user_agent: str = None,
                        endpoint: str = None, method: str = None, details: dict = None, status: str = "success"):
        """Log audit event"""
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            resource=resource,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            endpoint=endpoint,
            method=method,
            details=json.dumps(details) if details else None,
            status=status
        )
        
        self.db.add(audit_log)
        # Note: Commit is handled by the calling method

    def setup_2fa(self, user: User) -> dict:
        """Setup two-factor authentication for user"""
        if user.is_2fa_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Two-factor authentication is already enabled"
            )

        # Generate TOTP secret
        secret = pyotp.random_base32()

        # Generate QR code
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=user.email,
            issuer_name=settings.TOTP_ISSUER
        )

        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        qr_code_data = base64.b64encode(buffer.getvalue()).decode()

        # Generate backup codes
        backup_codes = [secrets.token_hex(4).upper() for _ in range(10)]

        # Store secret temporarily (will be confirmed when user verifies)
        user.totp_secret = secret
        user.backup_codes = json.dumps(backup_codes)
        self.db.commit()

        return {
            "secret": secret,
            "qr_code": f"data:image/png;base64,{qr_code_data}",
            "backup_codes": backup_codes
        }

    def verify_2fa_setup(self, user: User, code: str) -> bool:
        """Verify 2FA setup with TOTP code"""
        if not user.totp_secret:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Two-factor authentication setup not initiated"
            )

        totp = pyotp.TOTP(user.totp_secret)
        if totp.verify(code):
            user.is_2fa_enabled = True
            self.db.commit()

            self._log_audit_event(
                user_id=user.id,
                action="2fa_enabled",
                status="success"
            )
            return True

        return False

    def verify_2fa_code(self, user: User, code: str) -> bool:
        """Verify 2FA code during login"""
        if not user.is_2fa_enabled or not user.totp_secret:
            return False

        # Check TOTP code
        totp = pyotp.TOTP(user.totp_secret)
        if totp.verify(code):
            return True

        # Check backup codes
        if user.backup_codes:
            backup_codes = json.loads(user.backup_codes)
            if code.upper() in backup_codes:
                # Remove used backup code
                backup_codes.remove(code.upper())
                user.backup_codes = json.dumps(backup_codes)
                self.db.commit()

                self._log_audit_event(
                    user_id=user.id,
                    action="2fa_backup_code_used",
                    details={"remaining_codes": len(backup_codes)},
                    status="success"
                )
                return True

        return False

    def disable_2fa(self, user: User, password: str, code: str) -> bool:
        """Disable two-factor authentication"""
        if not user.is_2fa_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Two-factor authentication is not enabled"
            )

        # Verify password
        if not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password is incorrect"
            )

        # Verify 2FA code
        if not self.verify_2fa_code(user, code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid two-factor authentication code"
            )

        # Disable 2FA
        user.is_2fa_enabled = False
        user.totp_secret = None
        user.backup_codes = None
        self.db.commit()

        self._log_audit_event(
            user_id=user.id,
            action="2fa_disabled",
            status="success"
        )

        return True
