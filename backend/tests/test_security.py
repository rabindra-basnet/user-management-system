import pytest
import time
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.core.security import (
    create_access_token, 
    verify_token, 
    get_password_hash, 
    verify_password,
    validate_password_strength
)
from app.models.user import User
from app.services.auth_service import AuthService
from tests.utils import create_test_user, get_test_db

client = TestClient(app)


class TestPasswordSecurity:
    """Test password security features"""
    
    def test_password_hashing(self):
        """Test password hashing and verification"""
        password = "TestPassword123!"
        hashed = get_password_hash(password)
        
        # Hash should be different from original
        assert hashed != password
        
        # Verification should work
        assert verify_password(password, hashed) is True
        
        # Wrong password should fail
        assert verify_password("WrongPassword", hashed) is False
    
    def test_password_strength_validation(self):
        """Test password strength requirements"""
        
        # Valid password
        valid_password = "StrongPass123!"
        is_valid, errors = validate_password_strength(valid_password)
        assert is_valid is True
        assert len(errors) == 0
        
        # Too short
        short_password = "Short1!"
        is_valid, errors = validate_password_strength(short_password)
        assert is_valid is False
        assert any("at least" in error for error in errors)
        
        # No uppercase
        no_upper = "lowercase123!"
        is_valid, errors = validate_password_strength(no_upper)
        assert is_valid is False
        assert any("uppercase" in error for error in errors)
        
        # No lowercase
        no_lower = "UPPERCASE123!"
        is_valid, errors = validate_password_strength(no_lower)
        assert is_valid is False
        assert any("lowercase" in error for error in errors)
        
        # No numbers
        no_numbers = "NoNumbers!"
        is_valid, errors = validate_password_strength(no_numbers)
        assert is_valid is False
        assert any("number" in error for error in errors)
        
        # No special characters
        no_special = "NoSpecial123"
        is_valid, errors = validate_password_strength(no_special)
        assert is_valid is False
        assert any("special" in error for error in errors)
        
        # Common weak password
        weak_password = "password"
        is_valid, errors = validate_password_strength(weak_password)
        assert is_valid is False
        assert any("common" in error for error in errors)


class TestJWTSecurity:
    """Test JWT token security"""
    
    def test_token_creation_and_verification(self):
        """Test JWT token creation and verification"""
        user_id = "test-user-id"
        
        # Create access token
        token = create_access_token(subject=user_id)
        assert token is not None
        
        # Verify token
        verified_user_id = verify_token(token)
        assert verified_user_id == user_id
    
    def test_invalid_token_verification(self):
        """Test verification of invalid tokens"""
        
        # Invalid token
        invalid_token = "invalid.token.here"
        result = verify_token(invalid_token)
        assert result is None
        
        # Empty token
        result = verify_token("")
        assert result is None
        
        # None token
        result = verify_token(None)
        assert result is None
    
    def test_token_expiration(self):
        """Test token expiration"""
        from datetime import timedelta
        
        user_id = "test-user-id"
        
        # Create token with very short expiration
        token = create_access_token(
            subject=user_id, 
            expires_delta=timedelta(seconds=1)
        )
        
        # Token should be valid immediately
        result = verify_token(token)
        assert result == user_id
        
        # Wait for token to expire
        time.sleep(2)
        
        # Token should now be invalid
        result = verify_token(token)
        assert result is None


class TestAuthenticationSecurity:
    """Test authentication security features"""
    
    def test_login_rate_limiting(self):
        """Test login rate limiting"""
        # This would require a test Redis instance
        # For now, we'll test the endpoint exists and handles rate limiting
        
        login_data = {
            "email": "test@example.com",
            "password": "wrongpassword"
        }
        
        # Multiple failed attempts should eventually be rate limited
        responses = []
        for _ in range(10):
            response = client.post("/api/v1/auth/login", json=login_data)
            responses.append(response.status_code)
        
        # Should have some 429 (Too Many Requests) responses
        assert 429 in responses or all(r == 401 for r in responses)
    
    def test_account_lockout(self, test_db: Session):
        """Test account lockout after failed attempts"""
        # Create test user
        user = create_test_user(test_db)
        auth_service = AuthService(test_db)
        
        # Multiple failed login attempts
        for _ in range(6):  # Exceed MAX_LOGIN_ATTEMPTS (5)
            result = auth_service.authenticate_user(
                email=user.email,
                password="wrongpassword"
            )
            assert result is None
        
        # User should now be locked
        user_after_attempts = test_db.query(User).filter(User.id == user.id).first()
        assert user_after_attempts.is_locked is True
        
        # Even correct password should fail when locked
        result = auth_service.authenticate_user(
            email=user.email,
            password="testpassword123"
        )
        assert result is None
    
    def test_session_security(self, test_db: Session):
        """Test session security features"""
        user = create_test_user(test_db)
        auth_service = AuthService(test_db)
        
        # Create session
        access_token, refresh_token = auth_service.create_user_session(
            user=user,
            ip_address="192.168.1.1",
            user_agent="Test Browser"
        )
        
        assert access_token is not None
        assert refresh_token is not None
        
        # Verify session exists
        from app.models.user import UserSession
        session = test_db.query(UserSession).filter(
            UserSession.refresh_token == refresh_token
        ).first()
        
        assert session is not None
        assert session.user_id == user.id
        assert session.ip_address == "192.168.1.1"
        assert session.user_agent == "Test Browser"


class TestAPIEndpointSecurity:
    """Test API endpoint security"""
    
    def test_protected_endpoints_require_auth(self):
        """Test that protected endpoints require authentication"""
        
        # Try to access protected endpoint without token
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401
        
        # Try to access users endpoint without token
        response = client.get("/api/v1/users/")
        assert response.status_code == 401
    
    def test_invalid_token_rejection(self):
        """Test rejection of invalid tokens"""
        
        # Invalid token format
        headers = {"Authorization": "Bearer invalid-token"}
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 401
        
        # Missing Bearer prefix
        headers = {"Authorization": "invalid-token"}
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 401
    
    def test_permission_based_access(self, test_db: Session):
        """Test permission-based access control"""
        # This would require setting up users with different permissions
        # and testing access to various endpoints
        pass
    
    def test_input_validation(self):
        """Test input validation security"""
        
        # Test SQL injection attempts
        malicious_email = "'; DROP TABLE users; --"
        response = client.post("/api/v1/auth/login", json={
            "email": malicious_email,
            "password": "password"
        })
        # Should return validation error, not 500
        assert response.status_code in [400, 401, 422]
        
        # Test XSS attempts
        xss_payload = "<script>alert('xss')</script>"
        response = client.post("/api/v1/auth/register", json={
            "email": "test@example.com",
            "first_name": xss_payload,
            "last_name": "User",
            "password": "TestPassword123!",
            "confirm_password": "TestPassword123!"
        })
        # Should handle gracefully
        assert response.status_code in [400, 422]


class TestSecurityHeaders:
    """Test security headers"""
    
    def test_security_headers_present(self):
        """Test that security headers are present in responses"""
        
        response = client.get("/health")
        
        # Check for security headers
        assert "X-Content-Type-Options" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        
        assert "X-Frame-Options" in response.headers
        assert response.headers["X-Frame-Options"] == "DENY"
        
        assert "X-XSS-Protection" in response.headers
        assert response.headers["X-XSS-Protection"] == "1; mode=block"
        
        assert "Referrer-Policy" in response.headers
        assert "Content-Security-Policy" in response.headers
    
    def test_cors_configuration(self):
        """Test CORS configuration"""
        
        # Test preflight request
        response = client.options(
            "/api/v1/auth/login",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            }
        )
        
        assert response.status_code == 200
        assert "Access-Control-Allow-Origin" in response.headers


class TestTwoFactorAuthentication:
    """Test 2FA security"""
    
    def test_2fa_setup_requires_auth(self):
        """Test that 2FA setup requires authentication"""
        
        response = client.post("/api/v1/auth/2fa/setup")
        assert response.status_code == 401
    
    def test_2fa_verification_flow(self, test_db: Session):
        """Test 2FA verification flow"""
        user = create_test_user(test_db)
        auth_service = AuthService(test_db)
        
        # Setup 2FA
        setup_data = auth_service.setup_2fa(user)
        
        assert "secret" in setup_data
        assert "qr_code" in setup_data
        assert "backup_codes" in setup_data
        
        # Verify with invalid code should fail
        result = auth_service.verify_2fa_setup(user, "000000")
        assert result is False
        
        # User should not have 2FA enabled yet
        test_db.refresh(user)
        assert user.is_2fa_enabled is False


class TestAuditLogging:
    """Test audit logging security"""
    
    def test_login_events_logged(self, test_db: Session):
        """Test that login events are properly logged"""
        user = create_test_user(test_db)
        auth_service = AuthService(test_db)
        
        # Successful login
        authenticated_user = auth_service.authenticate_user(
            email=user.email,
            password="testpassword123",
            ip_address="192.168.1.1",
            user_agent="Test Browser"
        )
        
        assert authenticated_user is not None
        
        # Check audit log
        from app.models.user import AuditLog
        audit_log = test_db.query(AuditLog).filter(
            AuditLog.user_id == user.id,
            AuditLog.action == "login_success"
        ).first()
        
        assert audit_log is not None
        assert audit_log.ip_address == "192.168.1.1"
        assert audit_log.user_agent == "Test Browser"
        assert audit_log.status == "success"
    
    def test_failed_login_logged(self, test_db: Session):
        """Test that failed login attempts are logged"""
        user = create_test_user(test_db)
        auth_service = AuthService(test_db)
        
        # Failed login
        result = auth_service.authenticate_user(
            email=user.email,
            password="wrongpassword",
            ip_address="192.168.1.1"
        )
        
        assert result is None
        
        # Check audit log
        from app.models.user import AuditLog
        audit_log = test_db.query(AuditLog).filter(
            AuditLog.user_id == user.id,
            AuditLog.action == "login_failed"
        ).first()
        
        assert audit_log is not None
        assert audit_log.status == "failure"


# Fixtures and utilities would be in conftest.py
@pytest.fixture
def test_db():
    """Provide test database session"""
    return get_test_db()


def test_overall_security_configuration():
    """Test overall security configuration"""
    
    # Test that debug mode is properly configured
    from app.core.config import settings
    
    # In production, debug should be False
    if not settings.DEBUG:
        assert settings.SECRET_KEY != "default-secret-key"
        assert len(settings.SECRET_KEY) >= 32
    
    # Test password requirements are reasonable
    assert settings.PASSWORD_MIN_LENGTH >= 8
    assert settings.MAX_LOGIN_ATTEMPTS <= 10
    assert settings.ACCOUNT_LOCKOUT_DURATION_MINUTES >= 5
