"""
Organization management endpoints for SAAS multi-tenancy.

This router handles organization CRUD operations, member management,
invitations, and subscription management for the hotel booking SAAS platform.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select, and_, or_
from typing import List, Optional
from datetime import datetime, timedelta
import uuid
import secrets
import string

from app.core.database import get_session
from app.utils.dependencies import get_current_user, get_active_user
from app.models.user import User
from app.models.organization import (
    Organization,
    OrganizationMember,
    OrganizationInvitation,
    SubscriptionPlan,
    OrganizationStatus,
    OrganizationRole,
    InvitationStatus,
)
from app.models.property import Property
from app.models.booking import Booking
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationOut,
    OrganizationMemberCreate,
    OrganizationMemberUpdate,
    OrganizationMemberOut,
    OrganizationInvitationCreate,
    OrganizationInvitationOut,
    InvitationResponse,
    SubscriptionUpdate,
    OrganizationStats,
    OrganizationSwitch
)
from app.services.task_queue import enqueue_email
from app.core.config import settings
from app.utils.enums import BookingStatus

router = APIRouter(prefix="/organizations", tags=["organizations"])


# ============================================================
# 🏢 Organization CRUD Operations
# ============================================================

@router.post("", response_model=OrganizationOut, status_code=status.HTTP_201_CREATED)
def create_organization(
    payload: OrganizationCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
):
    """Create a new organization. User becomes the owner."""
    
    # Check if slug is already taken
    existing = session.exec(
        select(Organization).where(Organization.slug == payload.slug)
    ).first()
    if existing:
        raise HTTPException(
            status_code=400, 
            detail=f"Organization slug '{payload.slug}' is already taken"
        )
    
    # Set subscription limits based on plan
    limits = get_subscription_limits(payload.subscription_plan)
    
    # Create organization
    org = Organization(
        **payload.dict(),
        owner_id=current_user.id,
        max_properties=limits["max_properties"],
        max_users=limits["max_users"],
        max_rooms_per_property=limits["max_rooms_per_property"],
        trial_ends_at=datetime.utcnow() + timedelta(days=14) if payload.subscription_plan == SubscriptionPlan.FREE else None
    )
    session.add(org)
    session.commit()
    session.refresh(org)
    
    # Add creator as owner member
    member = OrganizationMember(
        organization_id=org.id,
        user_id=current_user.id,
        role=OrganizationRole.OWNER,
        can_manage_properties=True,
        can_manage_bookings=True,
        can_manage_users=True,
        can_view_analytics=True,
        can_manage_billing=True,
        joined_at=datetime.utcnow()
    )
    session.add(member)
    
    # Set as user's current organization
    current_user.current_organization_id = org.id
    session.add(current_user)
    
    session.commit()
    return org


@router.get("", response_model=List[OrganizationOut])
def list_my_organizations(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
):
    """List organizations where current user is a member."""
    
    # Get organization IDs where user is a member
    member_query = select(OrganizationMember.organization_id).where(
        and_(
            OrganizationMember.user_id == current_user.id,
            OrganizationMember.is_active == True
        )
    )
    org_ids = session.exec(member_query).all()
    
    if not org_ids:
        return []
    
    # Get organizations
    orgs = session.exec(
        select(Organization).where(
            and_(
                Organization.id.in_(org_ids),
                Organization.is_active == True
            )
        )
    ).all()
    
    return orgs


@router.get("/{org_id}", response_model=OrganizationOut)
def get_organization(
    org_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
):
    """Get organization details if user is a member."""
    
    org = session.get(Organization, org_id)
    if not org or not org.is_active:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Check if user is a member
    member = session.exec(
        select(OrganizationMember).where(
            and_(
                OrganizationMember.organization_id == org_id,
                OrganizationMember.user_id == current_user.id,
                OrganizationMember.is_active == True
            )
        )
    ).first()
    
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this organization")
    
    return org


@router.patch("/{org_id}", response_model=OrganizationOut)
def update_organization(
    org_id: uuid.UUID,
    payload: OrganizationUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
):
    """Update organization details. Requires admin permissions."""
    
    org, member = get_organization_and_check_permission(
        session, org_id, current_user.id, "can_manage_users"
    )
    
    # Update organization
    update_data = payload.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(org, field, value)
    
    org.updated_at = datetime.utcnow()
    session.add(org)
    session.commit()
    session.refresh(org)
    
    return org


@router.post("/{org_id}/switch")
def switch_organization(
    org_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
):
    """Switch user's current active organization."""
    
    # Check if user is a member
    member = session.exec(
        select(OrganizationMember).where(
            and_(
                OrganizationMember.organization_id == org_id,
                OrganizationMember.user_id == current_user.id,
                OrganizationMember.is_active == True
            )
        )
    ).first()
    
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this organization")
    
    # Update user's current organization
    current_user.current_organization_id = org_id
    session.add(current_user)
    session.commit()
    
    return {"detail": "Organization switched successfully"}


# ============================================================
# 👥 Member Management
# ============================================================

@router.get("/{org_id}/members", response_model=List[OrganizationMemberOut])
def list_organization_members(
    org_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
):
    """List all members of an organization."""
    
    org, member = get_organization_and_check_permission(
        session, org_id, current_user.id, "can_manage_users"
    )
    
    members = session.exec(
        select(OrganizationMember).where(
            OrganizationMember.organization_id == org_id
        )
    ).all()
    
    return members


@router.patch("/{org_id}/members/{member_id}", response_model=OrganizationMemberOut)
def update_member_permissions(
    org_id: uuid.UUID,
    member_id: uuid.UUID,
    payload: OrganizationMemberUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
):
    """Update member permissions within organization."""
    
    org, current_member = get_organization_and_check_permission(
        session, org_id, current_user.id, "can_manage_users"
    )
    
    # Get target member
    target_member = session.get(OrganizationMember, member_id)
    if not target_member or target_member.organization_id != org_id:
        raise HTTPException(status_code=404, detail="Member not found")
    
    # Prevent self-demotion from owner
    if (
        target_member.user_id == current_user.id
        and target_member.role == OrganizationRole.OWNER
        and payload.role
        and payload.role != OrganizationRole.OWNER
    ):
        raise HTTPException(
            status_code=400, 
            detail="Cannot demote yourself from owner role"
        )
    
    # Update member
    update_data = payload.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(target_member, field, value)
    
    session.add(target_member)
    session.commit()
    session.refresh(target_member)
    
    return target_member


@router.delete("/{org_id}/members/{member_id}")
def remove_member(
    org_id: uuid.UUID,
    member_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
):
    """Remove a member from organization."""
    
    org, current_member = get_organization_and_check_permission(
        session, org_id, current_user.id, "can_manage_users"
    )
    
    # Get target member
    target_member = session.get(OrganizationMember, member_id)
    if not target_member or target_member.organization_id != org_id:
        raise HTTPException(status_code=404, detail="Member not found")
    
    # Prevent removing the last owner
    if target_member.role == OrganizationRole.OWNER:
        owner_count = session.exec(
            select(OrganizationMember).where(
                and_(
                    OrganizationMember.organization_id == org_id,
                    OrganizationMember.role == OrganizationRole.OWNER,
                    OrganizationMember.is_active == True
                )
            )
        ).all()
        
        if len(owner_count) <= 1:
            raise HTTPException(
                status_code=400, 
                detail="Cannot remove the last owner of the organization"
            )
    
    session.delete(target_member)
    session.commit()
    
    return {"detail": "Member removed successfully"}


# ============================================================
# 📧 Invitation Management
# ============================================================

@router.post("/{org_id}/invitations", response_model=OrganizationInvitationOut)
def invite_user(
    org_id: uuid.UUID,
    payload: OrganizationInvitationCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
):
    """Invite a user to join the organization."""
    
    org, member = get_organization_and_check_permission(
        session, org_id, current_user.id, "can_manage_users"
    )
    
    # Check if user is already a member
    existing_member = session.exec(
        select(OrganizationMember).where(
            and_(
                OrganizationMember.organization_id == org_id,
                OrganizationMember.user_id.in_(
                    select(User.id).where(User.email == payload.email)
                )
            )
        )
    ).first()
    
    if existing_member:
        raise HTTPException(
            status_code=400, 
            detail="User is already a member of this organization"
        )
    
    # Check for existing pending invitation
    existing_invitation = session.exec(
        select(OrganizationInvitation).where(
            and_(
                OrganizationInvitation.organization_id == org_id,
                OrganizationInvitation.email == payload.email,
                OrganizationInvitation.status == InvitationStatus.PENDING
            )
        )
    ).first()
    
    if existing_invitation:
        raise HTTPException(
            status_code=400, 
            detail="Invitation already sent to this email"
        )
    
    # Generate invitation token
    token = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
    
    # Create invitation
    invitation = OrganizationInvitation(
        organization_id=org_id,
        email=payload.email,
        role=payload.role,
        invited_by=current_user.id,
        invitation_token=token,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    session.add(invitation)
    session.commit()
    session.refresh(invitation)
    
    # Send invitation email
    invitation_url = f"{settings.FRONTEND_URL}/invitations/{token}"
    
    html = f"""
    <div style="font-family: Arial, sans-serif; color:#1a202c;">
        <h2 style="color:#2b6cb0;">You're invited to join {org.name}</h2>
        <p>Hi there,</p>
        
        <p><strong>{current_user.full_name}</strong> has invited you to join 
        <strong>{org.name}</strong> as a <strong>{payload.role}</strong>.</p>
        
        <p>Click the button below to accept the invitation:</p>
        
        <a href="{invitation_url}"
           style="background:#38a169;color:#ffffff;padding:12px 24px;
                  text-decoration:none;border-radius:6px;display:inline-block;
                  font-weight:600;margin:16px 0;">
            Accept Invitation
        </a>
        
        <p>This invitation will expire in 7 days.</p>
        
        <hr style="border:none;border-top:1px solid #e2e8f0;margin:20px 0;" />
        <p style="font-size:12px;color:#718096;">
            If you don't want to join this organization, you can safely ignore this email.
        </p>
    </div>
    """
    
    enqueue_email(payload.email, f"Invitation to join {org.name}", html)
    
    return invitation


@router.get("/{org_id}/invitations", response_model=List[OrganizationInvitationOut])
def list_invitations(
    org_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
):
    """List all pending invitations for an organization."""
    
    org, member = get_organization_and_check_permission(
        session, org_id, current_user.id, "can_manage_users"
    )
    
    invitations = session.exec(
        select(OrganizationInvitation).where(
            OrganizationInvitation.organization_id == org_id
        )
    ).all()
    
    return invitations


@router.post("/invitations/{token}/respond")
def respond_to_invitation(
    token: str,
    payload: InvitationResponse,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
):
    """Accept or decline an organization invitation."""
    
    # Get invitation
    invitation = session.exec(
        select(OrganizationInvitation).where(
            OrganizationInvitation.invitation_token == token
        )
    ).first()
    
    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation not found")
    
    if invitation.status != InvitationStatus.PENDING:
        raise HTTPException(status_code=400, detail="Invitation already responded to")
    
    if invitation.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invitation has expired")
    
    if invitation.email != current_user.email:
        raise HTTPException(
            status_code=403, 
            detail="This invitation is not for your email address"
        )
    
    # Update invitation status
    invitation.status = (
        InvitationStatus.ACCEPTED if payload.action == "accept" else InvitationStatus.DECLINED
    )
    invitation.responded_at = datetime.utcnow()
    session.add(invitation)
    
    if payload.action == "accept":
        # Create organization membership
        member = OrganizationMember(
            organization_id=invitation.organization_id,
            user_id=current_user.id,
            role=invitation.role,
            joined_at=datetime.utcnow()
        )
        session.add(member)
        
        # Set as current organization if user doesn't have one
        if not current_user.current_organization_id:
            current_user.current_organization_id = invitation.organization_id
            session.add(current_user)
    
    session.commit()
    
    return {"detail": f"Invitation {payload.action}ed successfully"}


# ============================================================
# 📊 Organization Statistics
# ============================================================

@router.get("/{org_id}/stats", response_model=OrganizationStats)
def get_organization_stats(
    org_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
):
    """Get organization statistics and usage metrics."""
    
    org, member = get_organization_and_check_permission(
        session, org_id, current_user.id, "can_view_analytics"
    )
    
    # Count properties
    properties = session.exec(
        select(Property).where(Property.organization_id == org_id)
    ).all()
    total_properties = len(properties)
    
    # Count rooms (assuming rooms are linked to properties)
    total_rooms = 0  # Would need to implement room counting logic
    
    # Count bookings
    bookings = session.exec(
        select(Booking).where(
            Booking.property_id.in_([p.id for p in properties])
        )
    ).all()
    total_bookings = len(bookings)
    
    # Calculate revenue
    total_revenue = sum(b.total_amount for b in bookings)
    
    # Active bookings
    active_bookings = len(
        [
            b
            for b in bookings
            if b.status in [BookingStatus.PENDING, BookingStatus.CONFIRMED]
        ]
    )
    
    # Occupancy rate (simplified calculation)
    occupancy_rate = 0.0  # Would need more complex calculation
    
    # Count organization members
    members = session.exec(
        select(OrganizationMember).where(
            and_(
                OrganizationMember.organization_id == org_id,
                OrganizationMember.is_active == True
            )
        )
    ).all()
    users_used = len(members)
    
    return OrganizationStats(
        total_properties=total_properties,
        total_rooms=total_rooms,
        total_bookings=total_bookings,
        total_revenue=total_revenue,
        active_bookings=active_bookings,
        occupancy_rate=occupancy_rate,
        properties_used=total_properties,
        properties_limit=org.max_properties,
        users_used=users_used,
        users_limit=org.max_users
    )


# ============================================================
# 🔧 Helper Functions
# ============================================================

def get_subscription_limits(plan: SubscriptionPlan) -> dict:
    """Get limits based on subscription plan."""
    limits = {
        SubscriptionPlan.FREE: {
            "max_properties": 1,
            "max_users": 3,
            "max_rooms_per_property": 5
        },
        SubscriptionPlan.BASIC: {
            "max_properties": 5,
            "max_users": 10,
            "max_rooms_per_property": 20
        },
        SubscriptionPlan.PROFESSIONAL: {
            "max_properties": 25,
            "max_users": 50,
            "max_rooms_per_property": 100
        },
        SubscriptionPlan.ENTERPRISE: {
            "max_properties": 999,
            "max_users": 999,
            "max_rooms_per_property": 999
        }
    }
    return limits[plan]


def get_organization_and_check_permission(
    session: Session, 
    org_id: uuid.UUID, 
    user_id: uuid.UUID, 
    required_permission: str
) -> tuple[Organization, OrganizationMember]:
    """Get organization and check if user has required permission."""
    
    org = session.get(Organization, org_id)
    if not org or not org.is_active:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    member = session.exec(
        select(OrganizationMember).where(
            and_(
                OrganizationMember.organization_id == org_id,
                OrganizationMember.user_id == user_id,
                OrganizationMember.is_active == True
            )
        )
    ).first()
    
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this organization")
    
    # Check specific permission
    if required_permission and not getattr(member, required_permission, False):
        # Owners and admins have all permissions
        if member.role not in [OrganizationRole.OWNER, OrganizationRole.ADMIN]:
            raise HTTPException(
                status_code=403, 
                detail=f"Insufficient permissions: {required_permission} required"
            )
    
    return org, member
