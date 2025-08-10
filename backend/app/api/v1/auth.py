from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.api import deps
from app.core.config import settings
from app.core.security import create_access_token
from app.models.user import User
from app.schemas.user import (
    LoginRequest, LoginResponse, Token, TokenRefresh, UserCreate, User as UserSchema,
    PasswordChange, PasswordReset, TwoFactorSetup, TwoFactorVerify, TwoFactorDisable
)
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/register", response_model=UserSchema)
def register(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserCreate,
    request: Request,
    auth_service: AuthService = Depends(deps.get_auth_service),
    _: Any = Depends(deps.general_rate_limit)
) -> Any:
    """Register a new user"""
    
    ip_address = deps.get_client_ip(request)
    user_agent = deps.get_user_agent(request)
    
    user = auth_service.register_user(user_in, ip_address, user_agent)
    return user


@router.post("/login", response_model=LoginResponse)
def login(
    *,
    db: Session = Depends(deps.get_db),
    login_data: LoginRequest,
    request: Request,
    auth_service: AuthService = Depends(deps.get_auth_service),
    _: Any = Depends(deps.login_rate_limit)
) -> Any:
    """Login user and return access token"""
    
    ip_address = deps.get_client_ip(request)
    user_agent = deps.get_user_agent(request)
    
    # Authenticate user
    user = auth_service.authenticate_user(
        email=login_data.email,
        password=login_data.password,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Check if 2FA is enabled
    if user.is_2fa_enabled:
        # Return temporary token for 2FA verification
        temp_token = create_access_token(
            subject=f"2fa:{user.id}",
            expires_delta=timedelta(minutes=5)
        )
        return LoginResponse(
            user=user,
            token=Token(
                access_token=temp_token,
                refresh_token="",
                token_type="bearer",
                expires_in=300
            ),
            message="Two-factor authentication required"
        )
    
    # Create session and tokens
    access_token, refresh_token = auth_service.create_user_session(
        user=user,
        ip_address=ip_address,
        user_agent=user_agent,
        remember_me=login_data.remember_me
    )
    
    return LoginResponse(
        user=user,
        token=Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    )


@router.post("/login/2fa", response_model=LoginResponse)
def login_2fa(
    *,
    db: Session = Depends(deps.get_db),
    code_data: TwoFactorVerify,
    request: Request,
    auth_service: AuthService = Depends(deps.get_auth_service),
    _: Any = Depends(deps.login_rate_limit)
) -> Any:
    """Complete 2FA login"""
    
    # Get authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header"
        )
    
    token = auth_header.split(" ")[1]
    
    # Verify 2FA token
    from app.core.security import verify_token
    token_data = verify_token(token)
    if not token_data or not token_data.startswith("2fa:"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid 2FA token"
        )
    
    user_id = token_data.split(":")[1]
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Verify 2FA code
    if not auth_service.verify_2fa_code(user, code_data.code):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid two-factor authentication code"
        )
    
    # Create session and tokens
    ip_address = deps.get_client_ip(request)
    user_agent = deps.get_user_agent(request)
    
    access_token, refresh_token = auth_service.create_user_session(
        user=user,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    return LoginResponse(
        user=user,
        token=Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    )


@router.post("/refresh", response_model=Token)
def refresh_token(
    *,
    refresh_data: TokenRefresh,
    auth_service: AuthService = Depends(deps.get_auth_service),
    _: Any = Depends(deps.general_rate_limit)
) -> Any:
    """Refresh access token"""
    
    access_token = auth_service.refresh_access_token(refresh_data.refresh_token)
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_data.refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/logout")
def logout(
    *,
    refresh_data: TokenRefresh,
    request: Request,
    auth_service: AuthService = Depends(deps.get_auth_service)
) -> Any:
    """Logout user"""
    
    ip_address = deps.get_client_ip(request)
    user_agent = deps.get_user_agent(request)
    
    success = auth_service.logout_user(
        refresh_token=refresh_data.refresh_token,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    if success:
        return {"message": "Successfully logged out"}
    else:
        return {"message": "Already logged out"}


@router.post("/logout-all")
def logout_all(
    *,
    current_user: User = Depends(deps.get_current_user),
    auth_service: AuthService = Depends(deps.get_auth_service)
) -> Any:
    """Logout user from all sessions"""
    
    count = auth_service.logout_all_sessions(str(current_user.id))
    return {"message": f"Logged out from {count} sessions"}


@router.get("/me", response_model=UserSchema)
def read_users_me(
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """Get current user"""
    return current_user


@router.post("/change-password")
def change_password(
    *,
    password_data: PasswordChange,
    current_user: User = Depends(deps.get_current_user),
    auth_service: AuthService = Depends(deps.get_auth_service)
) -> Any:
    """Change user password"""
    
    auth_service.change_password(
        user=current_user,
        current_password=password_data.current_password,
        new_password=password_data.new_password
    )
    
    return {"message": "Password changed successfully"}


@router.post("/2fa/setup", response_model=TwoFactorSetup)
def setup_2fa(
    *,
    current_user: User = Depends(deps.get_current_user),
    auth_service: AuthService = Depends(deps.get_auth_service)
) -> Any:
    """Setup two-factor authentication"""
    
    setup_data = auth_service.setup_2fa(current_user)
    return TwoFactorSetup(**setup_data)


@router.post("/2fa/verify")
def verify_2fa_setup(
    *,
    code_data: TwoFactorVerify,
    current_user: User = Depends(deps.get_current_user),
    auth_service: AuthService = Depends(deps.get_auth_service)
) -> Any:
    """Verify and enable 2FA"""
    
    success = auth_service.verify_2fa_setup(current_user, code_data.code)
    if success:
        return {"message": "Two-factor authentication enabled successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code"
        )


@router.post("/2fa/disable")
def disable_2fa(
    *,
    disable_data: TwoFactorDisable,
    current_user: User = Depends(deps.get_current_user),
    auth_service: AuthService = Depends(deps.get_auth_service)
) -> Any:
    """Disable two-factor authentication"""
    
    success = auth_service.disable_2fa(
        user=current_user,
        password=disable_data.password,
        code=disable_data.code
    )
    
    if success:
        return {"message": "Two-factor authentication disabled successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to disable two-factor authentication"
        )
