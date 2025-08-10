from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.api import deps
from app.models.user import User, AuditLog
from app.schemas.user import AuditLog as AuditLogSchema
from app.services.user_service import UserService
from app.services.permission_service import PermissionService
import uuid

router = APIRouter()


@router.get("/statistics")
def get_system_statistics(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_permission("system.admin"))
) -> Any:
    """Get system statistics"""
    
    user_service = UserService(db)
    stats = user_service.get_user_statistics()
    
    # Add additional system stats
    from app.models.user import Role, Permission, UserSession
    
    stats.update({
        "total_roles": db.query(Role).count(),
        "total_permissions": db.query(Permission).count(),
        "active_sessions": db.query(UserSession).filter(UserSession.is_active == True).count(),
        "total_audit_logs": db.query(AuditLog).count()
    })
    
    return stats


@router.get("/audit-logs", response_model=List[AuditLogSchema])
def get_audit_logs(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    user_id: uuid.UUID = Query(None),
    action: str = Query(None),
    status: str = Query(None),
    current_user: User = Depends(deps.require_permission("audit.read"))
) -> Any:
    """Get audit logs with filtering"""
    
    query = db.query(AuditLog)
    
    # Apply filters
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    
    if action:
        query = query.filter(AuditLog.action.ilike(f"%{action}%"))
    
    if status:
        query = query.filter(AuditLog.status == status)
    
    # Apply pagination and ordering
    audit_logs = query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
    
    return audit_logs


@router.get("/active-sessions")
def get_active_sessions(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(deps.require_permission("system.admin"))
) -> Any:
    """Get active user sessions"""
    
    from app.models.user import UserSession
    
    sessions = db.query(UserSession).filter(
        UserSession.is_active == True
    ).order_by(UserSession.last_activity.desc()).offset(skip).limit(limit).all()
    
    session_data = []
    for session in sessions:
        session_data.append({
            "id": session.id,
            "user_id": session.user_id,
            "user_email": session.user.email if session.user else None,
            "user_name": f"{session.user.first_name} {session.user.last_name}" if session.user else None,
            "ip_address": session.ip_address,
            "user_agent": session.user_agent,
            "last_activity": session.last_activity,
            "created_at": session.created_at
        })
    
    return {
        "sessions": session_data,
        "total": db.query(UserSession).filter(UserSession.is_active == True).count()
    }


@router.delete("/sessions/{session_id}")
def revoke_session(
    *,
    db: Session = Depends(deps.get_db),
    session_id: uuid.UUID,
    current_user: User = Depends(deps.require_permission("system.admin"))
) -> Any:
    """Revoke a user session"""
    
    from app.models.user import UserSession
    
    session = db.query(UserSession).filter(UserSession.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    session.is_active = False
    db.commit()
    
    return {"message": "Session revoked successfully"}


@router.post("/users/{user_id}/force-logout")
def force_user_logout(
    *,
    db: Session = Depends(deps.get_db),
    user_id: uuid.UUID,
    current_user: User = Depends(deps.require_permission("system.admin"))
) -> Any:
    """Force logout a user from all sessions"""
    
    from app.models.user import UserSession
    
    # Check if user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Deactivate all user sessions
    sessions_updated = db.query(UserSession).filter(
        UserSession.user_id == user_id,
        UserSession.is_active == True
    ).update({"is_active": False})
    
    db.commit()
    
    return {
        "message": f"User {user.email} logged out from all sessions",
        "sessions_revoked": sessions_updated
    }


@router.get("/security-report")
def get_security_report(
    *,
    db: Session = Depends(deps.get_db),
    days: int = Query(7, ge=1, le=30),
    current_user: User = Depends(deps.require_permission("system.admin"))
) -> Any:
    """Get security report for the last N days"""
    
    from datetime import datetime, timedelta
    from sqlalchemy import func
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Failed login attempts
    failed_logins = db.query(AuditLog).filter(
        AuditLog.action == "login_failed",
        AuditLog.created_at >= start_date
    ).count()
    
    # Successful logins
    successful_logins = db.query(AuditLog).filter(
        AuditLog.action == "login_success",
        AuditLog.created_at >= start_date
    ).count()
    
    # Account lockouts
    account_lockouts = db.query(AuditLog).filter(
        AuditLog.action == "account_locked",
        AuditLog.created_at >= start_date
    ).count()
    
    # Password changes
    password_changes = db.query(AuditLog).filter(
        AuditLog.action == "password_changed",
        AuditLog.created_at >= start_date
    ).count()
    
    # 2FA events
    twofa_enabled = db.query(AuditLog).filter(
        AuditLog.action == "2fa_enabled",
        AuditLog.created_at >= start_date
    ).count()
    
    twofa_disabled = db.query(AuditLog).filter(
        AuditLog.action == "2fa_disabled",
        AuditLog.created_at >= start_date
    ).count()
    
    # Top IP addresses with failed attempts
    top_failed_ips = db.query(
        AuditLog.ip_address,
        func.count(AuditLog.id).label('count')
    ).filter(
        AuditLog.action == "login_failed",
        AuditLog.created_at >= start_date,
        AuditLog.ip_address.isnot(None)
    ).group_by(AuditLog.ip_address).order_by(func.count(AuditLog.id).desc()).limit(10).all()
    
    return {
        "period_days": days,
        "start_date": start_date,
        "end_date": datetime.utcnow(),
        "login_attempts": {
            "successful": successful_logins,
            "failed": failed_logins,
            "success_rate": round((successful_logins / max(successful_logins + failed_logins, 1)) * 100, 2)
        },
        "security_events": {
            "account_lockouts": account_lockouts,
            "password_changes": password_changes,
            "twofa_enabled": twofa_enabled,
            "twofa_disabled": twofa_disabled
        },
        "top_failed_ips": [
            {"ip_address": ip, "failed_attempts": count}
            for ip, count in top_failed_ips
        ]
    }


@router.post("/cleanup-sessions")
def cleanup_expired_sessions(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_permission("system.admin"))
) -> Any:
    """Clean up expired sessions"""
    
    from datetime import datetime
    from app.models.user import UserSession
    
    # Deactivate expired sessions
    expired_sessions = db.query(UserSession).filter(
        UserSession.expires_at < datetime.utcnow(),
        UserSession.is_active == True
    ).update({"is_active": False})
    
    db.commit()
    
    return {
        "message": "Expired sessions cleaned up",
        "sessions_cleaned": expired_sessions
    }


@router.get("/system-health")
def get_system_health(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_permission("system.admin"))
) -> Any:
    """Get system health status"""
    
    try:
        # Test database connection
        db.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    # Test Redis connection (if available)
    redis_status = "healthy"
    try:
        from app.api.deps import redis_client
        redis_client.ping()
    except Exception as e:
        redis_status = f"error: {str(e)}"
    
    return {
        "status": "healthy" if db_status == "healthy" and redis_status == "healthy" else "degraded",
        "database": db_status,
        "redis": redis_status,
        "timestamp": datetime.utcnow()
    }
