from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.db.base_class import Base
from app.models.user import User, Role, Permission
from app.core.security import get_password_hash
import uuid

# Test database URL (use in-memory SQLite for tests)
TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_test_db() -> Session:
    """Get test database session"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        return db
    finally:
        db.close()


def create_test_user(db: Session, **kwargs) -> User:
    """Create a test user"""
    user_data = {
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "hashed_password": get_password_hash("testpassword123"),
        "is_active": True,
        "is_verified": True,
        **kwargs
    }
    
    user = User(**user_data)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_test_role(db: Session, **kwargs) -> Role:
    """Create a test role"""
    role_data = {
        "name": "Test Role",
        "description": "Test role for testing",
        **kwargs
    }
    
    role = Role(**role_data)
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


def create_test_permission(db: Session, **kwargs) -> Permission:
    """Create a test permission"""
    permission_data = {
        "name": "test.permission",
        "description": "Test permission",
        "resource": "test",
        "action": "read",
        **kwargs
    }
    
    permission = Permission(**permission_data)
    db.add(permission)
    db.commit()
    db.refresh(permission)
    return permission


def cleanup_test_db():
    """Clean up test database"""
    Base.metadata.drop_all(bind=engine)
