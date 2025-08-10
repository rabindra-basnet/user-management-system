from fastapi import Request, HTTPException, status
from fastapi.middleware.base import BaseHTTPMiddleware
import redis
import time
import json
from typing import Dict, Optional
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Advanced rate limiting middleware with Redis backend"""
    
    def __init__(self, app, redis_url: str = None):
        super().__init__(app)
        self.redis_url = redis_url or settings.REDIS_URL
        self.redis_client = None
        self.fallback_storage: Dict[str, Dict] = {}  # In-memory fallback
        
        try:
            self.redis_client = redis.from_url(self.redis_url)
            self.redis_client.ping()
            logger.info("Redis connected for rate limiting")
        except Exception as e:
            logger.warning(f"Redis connection failed, using in-memory storage: {e}")
    
    async def dispatch(self, request: Request, call_next):
        # Get rate limit configuration for this endpoint
        rate_limit_config = self.get_rate_limit_config(request)
        
        if rate_limit_config:
            client_id = self.get_client_identifier(request)
            
            # Check rate limit
            if not await self.check_rate_limit(client_id, rate_limit_config):
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded. Please try again later.",
                    headers={"Retry-After": str(rate_limit_config["window"])}
                )
        
        response = await call_next(request)
        
        # Add rate limit headers
        if rate_limit_config:
            remaining, reset_time = await self.get_rate_limit_info(client_id, rate_limit_config)
            response.headers["X-RateLimit-Limit"] = str(rate_limit_config["requests"])
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            response.headers["X-RateLimit-Reset"] = str(reset_time)
        
        return response
    
    def get_rate_limit_config(self, request: Request) -> Optional[Dict]:
        """Get rate limit configuration for the current endpoint"""
        
        path = request.url.path
        method = request.method
        
        # Define rate limits for different endpoints
        rate_limits = {
            # Authentication endpoints (stricter limits)
            ("POST", "/api/v1/auth/login"): {"requests": 5, "window": 300},  # 5 per 5 minutes
            ("POST", "/api/v1/auth/register"): {"requests": 3, "window": 3600},  # 3 per hour
            ("POST", "/api/v1/auth/refresh"): {"requests": 10, "window": 300},  # 10 per 5 minutes
            ("POST", "/api/v1/auth/2fa/verify"): {"requests": 5, "window": 300},  # 5 per 5 minutes
            
            # Password related (very strict)
            ("POST", "/api/v1/auth/change-password"): {"requests": 3, "window": 3600},  # 3 per hour
            ("POST", "/api/v1/auth/forgot-password"): {"requests": 3, "window": 3600},  # 3 per hour
            
            # User management (moderate limits)
            ("POST", "/api/v1/users/"): {"requests": 10, "window": 3600},  # 10 per hour
            ("PUT", "/api/v1/users/*"): {"requests": 20, "window": 3600},  # 20 per hour
            ("DELETE", "/api/v1/users/*"): {"requests": 5, "window": 3600},  # 5 per hour
            
            # General API (lenient limits)
            ("GET", "/api/v1/*"): {"requests": 100, "window": 300},  # 100 per 5 minutes
            ("POST", "/api/v1/*"): {"requests": 50, "window": 300},  # 50 per 5 minutes
            ("PUT", "/api/v1/*"): {"requests": 50, "window": 300},  # 50 per 5 minutes
            ("DELETE", "/api/v1/*"): {"requests": 20, "window": 300},  # 20 per 5 minutes
        }
        
        # Find matching rate limit
        for (limit_method, limit_path), config in rate_limits.items():
            if method == limit_method:
                if limit_path == path:
                    return config
                elif limit_path.endswith("*") and path.startswith(limit_path[:-1]):
                    return config
        
        return None
    
    def get_client_identifier(self, request: Request) -> str:
        """Get unique identifier for the client"""
        
        # Try to get user ID from token if authenticated
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            try:
                from app.core.security import verify_token
                token = auth_header.split(" ")[1]
                user_id = verify_token(token)
                if user_id:
                    return f"user:{user_id}"
            except:
                pass
        
        # Fall back to IP address
        ip = self.get_client_ip(request)
        return f"ip:{ip}"
    
    def get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    async def check_rate_limit(self, client_id: str, config: Dict) -> bool:
        """Check if client is within rate limit"""
        
        key = f"rate_limit:{client_id}:{config['window']}"
        current_time = int(time.time())
        window_start = current_time - config["window"]
        
        if self.redis_client:
            try:
                return await self.check_rate_limit_redis(key, window_start, current_time, config)
            except Exception as e:
                logger.warning(f"Redis rate limit check failed: {e}")
                return self.check_rate_limit_memory(key, window_start, current_time, config)
        else:
            return self.check_rate_limit_memory(key, window_start, current_time, config)
    
    async def check_rate_limit_redis(self, key: str, window_start: int, current_time: int, config: Dict) -> bool:
        """Check rate limit using Redis"""
        
        pipe = self.redis_client.pipeline()
        
        # Remove old entries
        pipe.zremrangebyscore(key, 0, window_start)
        
        # Count current requests
        pipe.zcard(key)
        
        # Add current request
        pipe.zadd(key, {str(current_time): current_time})
        
        # Set expiration
        pipe.expire(key, config["window"])
        
        results = pipe.execute()
        current_requests = results[1]
        
        return current_requests < config["requests"]
    
    def check_rate_limit_memory(self, key: str, window_start: int, current_time: int, config: Dict) -> bool:
        """Check rate limit using in-memory storage"""
        
        if key not in self.fallback_storage:
            self.fallback_storage[key] = {"requests": [], "expires": current_time + config["window"]}
        
        storage = self.fallback_storage[key]
        
        # Clean expired entries
        if current_time > storage["expires"]:
            self.fallback_storage[key] = {"requests": [], "expires": current_time + config["window"]}
            storage = self.fallback_storage[key]
        
        # Remove old requests
        storage["requests"] = [req_time for req_time in storage["requests"] if req_time > window_start]
        
        # Check limit
        if len(storage["requests"]) >= config["requests"]:
            return False
        
        # Add current request
        storage["requests"].append(current_time)
        return True
    
    async def get_rate_limit_info(self, client_id: str, config: Dict) -> tuple:
        """Get remaining requests and reset time"""
        
        key = f"rate_limit:{client_id}:{config['window']}"
        current_time = int(time.time())
        window_start = current_time - config["window"]
        
        if self.redis_client:
            try:
                # Count current requests
                current_requests = self.redis_client.zcount(key, window_start, current_time)
                remaining = max(0, config["requests"] - current_requests)
                reset_time = current_time + config["window"]
                return remaining, reset_time
            except:
                pass
        
        # Fallback to memory
        if key in self.fallback_storage:
            storage = self.fallback_storage[key]
            current_requests = len([req for req in storage["requests"] if req > window_start])
            remaining = max(0, config["requests"] - current_requests)
            reset_time = storage["expires"]
            return remaining, reset_time
        
        return config["requests"], current_time + config["window"]


class IPWhitelistMiddleware(BaseHTTPMiddleware):
    """IP whitelist middleware for admin endpoints"""
    
    def __init__(self, app, whitelist: list = None, admin_paths: list = None):
        super().__init__(app)
        self.whitelist = set(whitelist or [])
        self.admin_paths = admin_paths or ["/api/v1/admin"]
        
        # Add localhost and common development IPs
        self.whitelist.update(["127.0.0.1", "::1", "localhost"])
    
    async def dispatch(self, request: Request, call_next):
        # Check if this is an admin path
        is_admin_path = any(request.url.path.startswith(path) for path in self.admin_paths)
        
        if is_admin_path and self.whitelist:
            client_ip = self.get_client_ip(request)
            
            if client_ip not in self.whitelist:
                logger.warning(f"Blocked admin access from non-whitelisted IP: {client_ip}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: IP not whitelisted for admin access"
                )
        
        return await call_next(request)
    
    def get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"


class RequestValidationMiddleware(BaseHTTPMiddleware):
    """Request validation middleware for security"""
    
    def __init__(self, app, max_request_size: int = 10 * 1024 * 1024):  # 10MB
        super().__init__(app)
        self.max_request_size = max_request_size
    
    async def dispatch(self, request: Request, call_next):
        # Check request size
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.max_request_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Request entity too large"
            )
        
        # Check for suspicious patterns in URL
        suspicious_patterns = [
            "../", "..\\", "/etc/passwd", "/proc/", "cmd.exe", "powershell",
            "<script", "javascript:", "vbscript:", "onload=", "onerror="
        ]
        
        url_path = str(request.url.path).lower()
        query_string = str(request.url.query).lower()
        
        for pattern in suspicious_patterns:
            if pattern in url_path or pattern in query_string:
                logger.warning(f"Suspicious request pattern detected: {pattern} in {request.url}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid request"
                )
        
        return await call_next(request)
