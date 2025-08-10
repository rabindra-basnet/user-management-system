from fastapi import Request, HTTPException, status
from fastapi.middleware.base import BaseHTTPMiddleware
import re
import json
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class InputSanitizationMiddleware(BaseHTTPMiddleware):
    """Middleware for input sanitization and validation"""
    
    def __init__(self, app):
        super().__init__(app)
        
        # Common XSS patterns
        self.xss_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'vbscript:',
            r'onload\s*=',
            r'onerror\s*=',
            r'onclick\s*=',
            r'onmouseover\s*=',
            r'<iframe[^>]*>.*?</iframe>',
            r'<object[^>]*>.*?</object>',
            r'<embed[^>]*>.*?</embed>',
            r'<link[^>]*>',
            r'<meta[^>]*>',
        ]
        
        # SQL injection patterns
        self.sql_patterns = [
            r'(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)',
            r'(\b(OR|AND)\s+\d+\s*=\s*\d+)',
            r'(\b(OR|AND)\s+[\'"][^\'"]*[\'"])',
            r'(--|#|/\*|\*/)',
            r'(\bUNION\s+SELECT\b)',
            r'(\bINTO\s+OUTFILE\b)',
            r'(\bLOAD_FILE\b)',
        ]
        
        # Path traversal patterns
        self.path_traversal_patterns = [
            r'\.\./+',
            r'\.\.\\+',
            r'/etc/passwd',
            r'/proc/',
            r'\\windows\\',
            r'\\system32\\',
        ]
        
        # Command injection patterns
        self.command_injection_patterns = [
            r'[;&|`$]',
            r'\b(cat|ls|dir|type|copy|del|rm|mv|cp)\b',
            r'\b(wget|curl|nc|netcat)\b',
            r'\b(python|perl|ruby|php|bash|sh|cmd|powershell)\b',
        ]
    
    async def dispatch(self, request: Request, call_next):
        # Skip validation for certain content types
        content_type = request.headers.get("content-type", "")
        if content_type.startswith("multipart/form-data"):
            return await call_next(request)
        
        # Validate URL path and query parameters
        self.validate_url(request)
        
        # Validate request body for JSON requests
        if content_type.startswith("application/json"):
            await self.validate_json_body(request)
        
        return await call_next(request)
    
    def validate_url(self, request: Request):
        """Validate URL path and query parameters"""
        
        url_path = str(request.url.path)
        query_string = str(request.url.query)
        
        # Check for path traversal
        for pattern in self.path_traversal_patterns:
            if re.search(pattern, url_path, re.IGNORECASE):
                logger.warning(f"Path traversal attempt detected: {url_path}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid path"
                )
        
        # Check query parameters
        if query_string:
            for pattern in self.xss_patterns + self.sql_patterns + self.command_injection_patterns:
                if re.search(pattern, query_string, re.IGNORECASE):
                    logger.warning(f"Malicious query parameter detected: {query_string}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid query parameters"
                    )
    
    async def validate_json_body(self, request: Request):
        """Validate JSON request body"""
        
        try:
            # Read body
            body = await request.body()
            if not body:
                return
            
            # Parse JSON
            try:
                json_data = json.loads(body)
            except json.JSONDecodeError:
                return  # Let FastAPI handle JSON parsing errors
            
            # Validate JSON content
            self.validate_json_content(json_data)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error validating JSON body: {e}")
            # Don't block request for unexpected errors
    
    def validate_json_content(self, data: Any, path: str = ""):
        """Recursively validate JSON content"""
        
        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key
                self.validate_json_content(value, current_path)
        
        elif isinstance(data, list):
            for i, item in enumerate(data):
                current_path = f"{path}[{i}]"
                self.validate_json_content(item, current_path)
        
        elif isinstance(data, str):
            self.validate_string_content(data, path)
    
    def validate_string_content(self, content: str, path: str = ""):
        """Validate string content for malicious patterns"""
        
        # Check for XSS
        for pattern in self.xss_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                logger.warning(f"XSS attempt detected in {path}: {content[:100]}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid content in field: {path}"
                )
        
        # Check for SQL injection
        for pattern in self.sql_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                logger.warning(f"SQL injection attempt detected in {path}: {content[:100]}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid content in field: {path}"
                )
        
        # Check for command injection
        for pattern in self.command_injection_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                logger.warning(f"Command injection attempt detected in {path}: {content[:100]}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid content in field: {path}"
                )
        
        # Check for path traversal
        for pattern in self.path_traversal_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                logger.warning(f"Path traversal attempt detected in {path}: {content[:100]}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid content in field: {path}"
                )


class ContentTypeValidationMiddleware(BaseHTTPMiddleware):
    """Validate content types for security"""
    
    def __init__(self, app):
        super().__init__(app)
        
        # Allowed content types
        self.allowed_content_types = {
            "application/json",
            "application/x-www-form-urlencoded",
            "multipart/form-data",
            "text/plain",
            "image/jpeg",
            "image/png",
            "image/gif",
            "image/webp",
            "application/pdf",
        }
        
        # Dangerous content types
        self.dangerous_content_types = {
            "application/x-executable",
            "application/x-msdownload",
            "application/x-msdos-program",
            "application/x-winexe",
            "application/x-javascript",
            "text/javascript",
            "application/javascript",
            "text/html",
            "application/x-php",
            "application/x-httpd-php",
        }
    
    async def dispatch(self, request: Request, call_next):
        content_type = request.headers.get("content-type", "")
        
        # Extract base content type (remove charset, boundary, etc.)
        base_content_type = content_type.split(";")[0].strip().lower()
        
        # Skip validation for GET requests and empty content
        if request.method == "GET" or not base_content_type:
            return await call_next(request)
        
        # Check for dangerous content types
        if base_content_type in self.dangerous_content_types:
            logger.warning(f"Dangerous content type detected: {base_content_type}")
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="Unsupported or dangerous content type"
            )
        
        # For file uploads, be more restrictive
        if base_content_type == "multipart/form-data":
            # Additional validation would be done in the endpoint
            pass
        elif base_content_type not in self.allowed_content_types:
            logger.warning(f"Unsupported content type: {base_content_type}")
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="Unsupported content type"
            )
        
        return await call_next(request)


class FileUploadValidationMiddleware(BaseHTTPMiddleware):
    """Validate file uploads for security"""
    
    def __init__(self, app, max_file_size: int = 10 * 1024 * 1024):  # 10MB
        super().__init__(app)
        self.max_file_size = max_file_size
        
        # Allowed file extensions
        self.allowed_extensions = {
            ".jpg", ".jpeg", ".png", ".gif", ".webp",  # Images
            ".pdf", ".txt", ".csv", ".json",  # Documents
        }
        
        # Dangerous file extensions
        self.dangerous_extensions = {
            ".exe", ".bat", ".cmd", ".com", ".scr", ".pif",  # Executables
            ".js", ".vbs", ".ps1", ".sh", ".php", ".asp",  # Scripts
            ".dll", ".sys", ".msi", ".jar",  # System files
        }
        
        # Magic bytes for file type validation
        self.magic_bytes = {
            b'\xFF\xD8\xFF': 'jpg',
            b'\x89PNG\r\n\x1a\n': 'png',
            b'GIF87a': 'gif',
            b'GIF89a': 'gif',
            b'RIFF': 'webp',  # WebP files start with RIFF
            b'%PDF': 'pdf',
        }
    
    async def dispatch(self, request: Request, call_next):
        content_type = request.headers.get("content-type", "")
        
        # Only validate multipart/form-data (file uploads)
        if not content_type.startswith("multipart/form-data"):
            return await call_next(request)
        
        # File validation would typically be done in the endpoint
        # This middleware provides the validation utilities
        
        return await call_next(request)
    
    def validate_file(self, filename: str, content: bytes) -> bool:
        """Validate uploaded file"""
        
        # Check file size
        if len(content) > self.max_file_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File too large"
            )
        
        # Check file extension
        file_ext = self.get_file_extension(filename)
        
        if file_ext in self.dangerous_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Dangerous file type"
            )
        
        if file_ext not in self.allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File type not allowed"
            )
        
        # Validate file content (magic bytes)
        if not self.validate_file_content(content, file_ext):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File content does not match extension"
            )
        
        return True
    
    def get_file_extension(self, filename: str) -> str:
        """Get file extension in lowercase"""
        return filename.lower().split('.')[-1] if '.' in filename else ''
    
    def validate_file_content(self, content: bytes, expected_ext: str) -> bool:
        """Validate file content matches extension using magic bytes"""
        
        if not content:
            return False
        
        # Check magic bytes
        for magic, file_type in self.magic_bytes.items():
            if content.startswith(magic):
                # Map file types to extensions
                type_to_ext = {
                    'jpg': 'jpg',
                    'png': 'png', 
                    'gif': 'gif',
                    'webp': 'webp',
                    'pdf': 'pdf'
                }
                
                expected_type = type_to_ext.get(expected_ext)
                return file_type == expected_type
        
        # For text files, check if content is valid text
        if expected_ext in ['txt', 'csv', 'json']:
            try:
                content.decode('utf-8')
                return True
            except UnicodeDecodeError:
                return False
        
        return False
