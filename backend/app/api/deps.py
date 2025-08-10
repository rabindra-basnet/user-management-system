from typing import Generator, Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.core.security import verify_token
from app.models.user import User
from app.services.auth_service import AuthService
import redis
from app.core.config import settings

# Security scheme
security = HTTPBearer()

# Redis client for rate limiting
redis_client = redis.from_url(settings.REDIS_URL)


def get_db() -> Generator:
    """Get database session"""
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_current_user(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """Get current authenticated user"""
    
    # Verify token
    user_id = verify_token(credentials.credentials)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


def get_current_superuser(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current superuser"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


def get_optional_current_user(
    db: Session = Depends(get_db),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[User]:
    """Get current user if authenticated, otherwise None"""
    if credentials is None:
        return None
    
    try:
        user_id = verify_token(credentials.credentials)
        if user_id is None:
            return None
        
        user = db.query(User).filter(User.id == user_id).first()
        if user is None or not user.is_active:
            return None
        
        return user
    except:
        return None


def require_permission(permission: str):
    """Dependency factory for permission checking"""
    def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        if not current_user.has_permission(permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' required"
            )
        return current_user
    return permission_checker


def require_role(role: str):
    """Dependency factory for role checking"""
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if not current_user.has_role(role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{role}' required"
            )
        return current_user
    return role_checker


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """Get authentication service"""
    return AuthService(db)


def get_client_ip(request: Request) -> str:
    """Get client IP address"""
    # Check for forwarded headers first (for reverse proxy setups)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fallback to direct connection
    return request.client.host if request.client else "unknown"


def get_user_agent(request: Request) -> str:
    """Get user agent string"""
    return request.headers.get("User-Agent", "unknown")


def rate_limit_key(request: Request, identifier: str = None) -> str:
    """Generate rate limit key"""
    if identifier:
        return f"rate_limit:{identifier}:{get_client_ip(request)}"
    return f"rate_limit:general:{get_client_ip(request)}"


def check_rate_limit(
    request: Request,
    max_requests: int = settings.RATE_LIMIT_PER_MINUTE,
    window_seconds: int = 60,
    identifier: str = None
) -> bool:
    """Check if request is within rate limit"""
    key = rate_limit_key(request, identifier)
    
    try:
        current = redis_client.get(key)
        if current is None:
            # First request in window
            redis_client.setex(key, window_seconds, 1)
            return True
        
        current_count = int(current)
        if current_count >= max_requests:
            return False
        
        # Increment counter
        redis_client.incr(key)
        return True
    
    except Exception:
        # If Redis is down, allow the request
        return True


def rate_limit_dependency(
    max_requests: int = settings.RATE_LIMIT_PER_MINUTE,
    window_seconds: int = 60,
    identifier: str = None
):
    """Rate limiting dependency factory"""
    def rate_limiter(request: Request):
        if not check_rate_limit(request, max_requests, window_seconds, identifier):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded"
            )
    return rate_limiter


# Common rate limiters
general_rate_limit = rate_limit_dependency()
login_rate_limit = rate_limit_dependency(
    max_requests=settings.LOGIN_RATE_LIMIT_PER_MINUTE,
    identifier="login"
)
