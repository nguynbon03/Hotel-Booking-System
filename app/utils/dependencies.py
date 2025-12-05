from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status, Request
from sqlmodel import Session, select, and_
from fastapi.security import OAuth2PasswordBearer, HTTPBearer
from typing import Optional
import uuid
from app.core.config import settings
from app.core.database import get_session
from app.core.redis import is_token_blacklisted
from app.models.user import User
from app.models.organization import Organization, OrganizationMember
from app.utils.enums import UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
optional_oauth2_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token or credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        if payload.get("scope") != "access":
            raise credentials_exception

        if is_token_blacklisted(token):
            raise HTTPException(status_code=401, detail="Token revoked")

        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user. Please contact administrator."
        )
    return current_user


def get_current_staff(current_user: User = Depends(get_active_user)) -> User:
    # Staff, admin_org và admin tổng đều có thể truy cập các route staff
    if current_user.role not in [UserRole.STAFF, UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Staff privileges required."
        )
    return current_user


def get_current_superuser(current_user: User = Depends(get_active_user)) -> User:
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action."
        )
    return current_user


# ============================================================
# 🏢 Multi-tenancy Dependencies
# ============================================================

def get_current_organization(
    current_user: User = Depends(get_active_user),
    session: Session = Depends(get_session)
) -> Optional[Organization]:
    """Get user's current active organization."""
    if not current_user.current_organization_id:
        return None
    
    org = session.get(Organization, current_user.current_organization_id)
    if not org or not org.is_active:
        # Clear invalid organization reference
        current_user.current_organization_id = None
        session.add(current_user)
        session.commit()
        return None
    
    return org


def require_organization(
    current_org: Optional[Organization] = Depends(get_current_organization)
) -> Organization:
    """Require user to have an active organization."""
    if not current_org:
        raise HTTPException(
            status_code=400,
            detail="No active organization. Please select or create an organization first."
        )
    return current_org


def get_organization_member(
    current_user: User = Depends(get_active_user),
    current_org: Organization = Depends(require_organization),
    session: Session = Depends(get_session)
) -> OrganizationMember:
    """Get current user's membership in the active organization."""
    member = session.exec(
        select(OrganizationMember).where(
            and_(
                OrganizationMember.organization_id == current_org.id,
                OrganizationMember.user_id == current_user.id,
                OrganizationMember.is_active == True
            )
        )
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=403,
            detail="You are not a member of the current organization."
        )
    
    return member


def require_org_permission(permission: str):
    """Decorator factory to require specific organization permission."""
    def dependency(
        member: OrganizationMember = Depends(get_organization_member)
    ) -> OrganizationMember:
        # Owners and admins have all permissions
        if member.role in ["OWNER", "ADMIN"]:
            return member
        
        # Check specific permission
        if not getattr(member, permission, False):
            raise HTTPException(
                status_code=403,
                detail=f"Insufficient permissions: {permission} required"
            )
        
        return member
    
    return dependency


# Specific permission dependencies
def require_manage_properties():
    return require_org_permission("can_manage_properties")


def require_manage_bookings():
    return require_org_permission("can_manage_bookings")


def require_manage_users():
    return require_org_permission("can_manage_users")


def require_view_analytics():
    return require_org_permission("can_view_analytics")


def require_manage_billing():
    return require_org_permission("can_manage_billing")


def get_current_user_optional(
    credentials: Optional[str] = Depends(optional_oauth2_scheme),
    session: Session = Depends(get_session)
) -> Optional[User]:
    """Get current user if authenticated, otherwise return None."""
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        if payload.get("scope") != "access":
            return None
        
        if is_token_blacklisted(token):
            return None
        
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        
        user = session.get(User, user_id)
        if not user or not user.is_active:
            return None
        
        return user
    except JWTError:
        return None


def get_organization_context(
    current_user: User = Depends(get_active_user),
    current_org: Organization = Depends(require_organization),
    member: OrganizationMember = Depends(get_organization_member),
    session: Session = Depends(get_session)
) -> dict:
    """Get complete organization context for the current user."""
    return {
        "user": current_user,
        "organization": current_org,
        "member": member,
        "session": session,
        "permissions": {
            "can_manage_properties": member.can_manage_properties or member.role in ["OWNER", "ADMIN"],
            "can_manage_bookings": member.can_manage_bookings or member.role in ["OWNER", "ADMIN"],
            "can_manage_users": member.can_manage_users or member.role in ["OWNER", "ADMIN"],
            "can_view_analytics": member.can_view_analytics or member.role in ["OWNER", "ADMIN"],
            "can_manage_billing": member.can_manage_billing or member.role in ["OWNER", "ADMIN"],
        }
    }
