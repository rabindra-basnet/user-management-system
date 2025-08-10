from fastapi import Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import time
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # HSTS (only in production with HTTPS)
        if not settings.DEBUG:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Content Security Policy
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )
        response.headers["Content-Security-Policy"] = csp
        
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests for security monitoring"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Get client info
        client_ip = self.get_client_ip(request)
        user_agent = request.headers.get("User-Agent", "unknown")
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log request
        log_data = {
            "method": request.method,
            "url": str(request.url),
            "client_ip": client_ip,
            "user_agent": user_agent,
            "status_code": response.status_code,
            "process_time": round(process_time, 4)
        }
        
        # Log level based on status code
        if response.status_code >= 500:
            logger.error("Request failed", extra=log_data)
        elif response.status_code >= 400:
            logger.warning("Client error", extra=log_data)
        else:
            logger.info("Request processed", extra=log_data)
        
        # Add processing time header
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
    
    def get_client_ip(self, request: Request) -> str:
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


class RequestSizeMiddleware(BaseHTTPMiddleware):
    """Limit request body size to prevent DoS attacks"""
    
    def __init__(self, app, max_size: int = 10 * 1024 * 1024):  # 10MB default
        super().__init__(app)
        self.max_size = max_size
    
    async def dispatch(self, request: Request, call_next):
        # Check content length
        content_length = request.headers.get("content-length")
        if content_length:
            content_length = int(content_length)
            if content_length > self.max_size:
                return JSONResponse(
                    status_code=413,
                    content={"detail": "Request entity too large"}
                )
        
        return await call_next(request)


class IPWhitelistMiddleware(BaseHTTPMiddleware):
    """Allow only whitelisted IPs for admin endpoints"""
    
    def __init__(self, app, whitelist: list = None, admin_paths: list = None):
        super().__init__(app)
        self.whitelist = whitelist or []
        self.admin_paths = admin_paths or ["/admin", "/api/v1/admin"]
    
    async def dispatch(self, request: Request, call_next):
        # Skip if no whitelist configured
        if not self.whitelist:
            return await call_next(request)
        
        # Check if this is an admin path
        is_admin_path = any(request.url.path.startswith(path) for path in self.admin_paths)
        
        if is_admin_path:
            client_ip = self.get_client_ip(request)
            if client_ip not in self.whitelist:
                logger.warning(f"Blocked admin access from non-whitelisted IP: {client_ip}")
                return JSONResponse(
                    status_code=403,
                    content={"detail": "Access denied"}
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


class SessionSecurityMiddleware(BaseHTTPMiddleware):
    """Add session security measures"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Set secure cookie attributes
        if hasattr(response, 'set_cookie'):
            # This would be used if we were setting cookies directly
            # For JWT tokens, this is handled by the frontend
            pass
        
        return response


class BruteForceProtectionMiddleware(BaseHTTPMiddleware):
    """Basic brute force protection"""
    
    def __init__(self, app):
        super().__init__(app)
        self.failed_attempts = {}  # In production, use Redis
        self.max_attempts = 10
        self.block_duration = 300  # 5 minutes
    
    async def dispatch(self, request: Request, call_next):
        client_ip = self.get_client_ip(request)
        
        # Check if IP is currently blocked
        if self.is_blocked(client_ip):
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many failed attempts. Please try again later."}
            )
        
        response = await call_next(request)
        
        # Track failed login attempts
        if (request.url.path.endswith("/login") and 
            request.method == "POST" and 
            response.status_code == 401):
            self.record_failed_attempt(client_ip)
        
        # Reset counter on successful login
        elif (request.url.path.endswith("/login") and 
              request.method == "POST" and 
              response.status_code == 200):
            self.reset_failed_attempts(client_ip)
        
        return response
    
    def get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    def is_blocked(self, ip: str) -> bool:
        """Check if IP is currently blocked"""
        if ip not in self.failed_attempts:
            return False
        
        attempts, last_attempt = self.failed_attempts[ip]
        
        # Check if block period has expired
        if time.time() - last_attempt > self.block_duration:
            del self.failed_attempts[ip]
            return False
        
        return attempts >= self.max_attempts
    
    def record_failed_attempt(self, ip: str):
        """Record a failed login attempt"""
        current_time = time.time()
        
        if ip in self.failed_attempts:
            attempts, _ = self.failed_attempts[ip]
            self.failed_attempts[ip] = (attempts + 1, current_time)
        else:
            self.failed_attempts[ip] = (1, current_time)
    
    def reset_failed_attempts(self, ip: str):
        """Reset failed attempts counter"""
        if ip in self.failed_attempts:
            del self.failed_attempts[ip]
