from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.core.config import settings
from app.models.user import User
from app.services.permission_service import PermissionService
from app.services.auth_service import AuthService
from app.core.security import get_password_hash
import logging

logger = logging.getLogger(__name__)


def init_db() -> None:
    """Initialize database with default data"""
    
    db = SessionLocal()
    try:
        # Create default permissions and roles
        permission_service = PermissionService(db)
        
        # Create default permissions
        logger.info("Creating default permissions...")
        permissions = permission_service.create_default_permissions()
        logger.info(f"Created {len(permissions)} permissions")
        
        # Create default roles
        logger.info("Creating default roles...")
        roles = permission_service.create_default_roles()
        logger.info(f"Created {len(roles)} roles")
        
        # Create superuser if it doesn't exist
        superuser = db.query(User).filter(User.email == settings.FIRST_SUPERUSER_EMAIL).first()
        if not superuser:
            logger.info("Creating superuser...")
            
            superuser = User(
                email=settings.FIRST_SUPERUSER_EMAIL,
                first_name="Super",
                last_name="Admin",
                hashed_password=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
                is_active=True,
                is_verified=True,
                is_superuser=True
            )
            
            # Assign Administrator role
            admin_role = permission_service.get_role_by_name("Administrator")
            if admin_role:
                superuser.roles.append(admin_role)
            
            db.add(superuser)
            db.commit()
            db.refresh(superuser)
            
            logger.info(f"Superuser created: {superuser.email}")
        else:
            logger.info("Superuser already exists")
            
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
