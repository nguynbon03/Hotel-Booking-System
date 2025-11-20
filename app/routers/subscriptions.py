"""
Subscription management endpoints for SAAS platform.

This router handles subscription lifecycle, billing, usage tracking,
and plan management for organizations.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List, Optional, Dict, Any
import uuid

from app.core.database import get_session
from app.services.subscription_service import SubscriptionService
from app.utils.dependencies import (
    get_active_user, 
    require_organization,
    require_manage_billing
)
from app.models.user import User
from app.models.organization import Organization
from app.models.subscription import BillingCycle

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


@router.get("/plans")
def get_available_plans():
    """Get list of available subscription plans with features and pricing."""
    
    plans = [
        {
            "name": "FREE",
            "display_name": "Free Plan",
            "price": 0.00,
            "currency": "USD",
            "billing_cycles": ["MONTHLY"],
            "features": {
                "properties_limit": 1,
                "users_limit": 3,
                "bookings_limit": 50,
                "features": ["Basic booking management", "Basic analytics", "Email support"]
            },
            "description": "Perfect for small properties getting started",
            "popular": False
        },
        {
            "name": "BASIC",
            "display_name": "Basic Plan",
            "price": 29.99,
            "currency": "USD",
            "billing_cycles": ["MONTHLY", "YEARLY"],
            "features": {
                "properties_limit": 5,
                "users_limit": 10,
                "bookings_limit": 500,
                "features": [
                    "Advanced booking management",
                    "Detailed analytics",
                    "Email support",
                    "Custom branding",
                    "Multi-property management"
                ]
            },
            "description": "Great for growing hotel businesses",
            "popular": True
        },
        {
            "name": "PROFESSIONAL",
            "display_name": "Professional Plan",
            "price": 99.99,
            "currency": "USD",
            "billing_cycles": ["MONTHLY", "YEARLY"],
            "features": {
                "properties_limit": 25,
                "users_limit": 50,
                "bookings_limit": 2000,
                "features": [
                    "All Basic features",
                    "Advanced analytics & reporting",
                    "Priority support",
                    "API access",
                    "Channel management",
                    "Revenue optimization"
                ]
            },
            "description": "For established hotel chains and property managers",
            "popular": False
        },
        {
            "name": "ENTERPRISE",
            "display_name": "Enterprise Plan",
            "price": 299.99,
            "currency": "USD",
            "billing_cycles": ["MONTHLY", "YEARLY"],
            "features": {
                "properties_limit": "Unlimited",
                "users_limit": "Unlimited",
                "bookings_limit": "Unlimited",
                "features": [
                    "All Professional features",
                    "Dedicated account manager",
                    "Custom integrations",
                    "White-label solution",
                    "Advanced security",
                    "SLA guarantee"
                ]
            },
            "description": "For large enterprises with complex needs",
            "popular": False
        }
    ]
    
    return {"plans": plans}


@router.post("", status_code=status.HTTP_201_CREATED)
def create_subscription(
    plan_name: str,
    billing_cycle: BillingCycle = BillingCycle.MONTHLY,
    trial_days: int = 14,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
    current_org: Organization = Depends(require_organization)
):
    """Create a new subscription for the current organization."""
    
    subscription_service = SubscriptionService(session)
    
    subscription = subscription_service.create_subscription(
        organization_id=current_org.id,
        plan_name=plan_name,
        billing_cycle=billing_cycle,
        trial_days=trial_days
    )
    
    return {
        "id": subscription.id,
        "plan_name": subscription.plan_name,
        "status": subscription.status,
        "billing_cycle": subscription.billing_cycle,
        "trial_end": subscription.trial_end,
        "current_period_end": subscription.current_period_end,
        "base_price": float(subscription.base_price),
        "currency": subscription.currency
    }


@router.get("/current")
def get_current_subscription(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
    current_org: Organization = Depends(require_organization)
):
    """Get current subscription details for the organization."""
    
    subscription_service = SubscriptionService(session)
    subscription = subscription_service.get_organization_subscription(current_org.id)
    
    if not subscription:
        return {"subscription": None, "message": "No active subscription"}
    
    return {
        "id": subscription.id,
        "plan_name": subscription.plan_name,
        "status": subscription.status,
        "billing_cycle": subscription.billing_cycle,
        "base_price": float(subscription.base_price),
        "currency": subscription.currency,
        "trial_start": subscription.trial_start,
        "trial_end": subscription.trial_end,
        "current_period_start": subscription.current_period_start,
        "current_period_end": subscription.current_period_end,
        "cancel_at_period_end": subscription.cancel_at_period_end,
        "cancelled_at": subscription.cancelled_at,
        "limits": {
            "properties": subscription.properties_limit,
            "users": subscription.users_limit,
            "bookings": subscription.bookings_limit
        }
    }


@router.get("/usage")
def get_usage_statistics(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
    current_org: Organization = Depends(require_organization)
):
    """Get current usage statistics against subscription limits."""
    
    subscription_service = SubscriptionService(session)
    usage = subscription_service.check_usage_limits(current_org.id)
    
    return usage


@router.patch("/upgrade")
def upgrade_subscription(
    new_plan_name: str,
    billing_cycle: Optional[BillingCycle] = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
    current_org: Organization = Depends(require_organization),
    member = Depends(require_manage_billing())
):
    """Upgrade or change subscription plan."""
    
    subscription_service = SubscriptionService(session)
    
    subscription = subscription_service.upgrade_subscription(
        organization_id=current_org.id,
        new_plan_name=new_plan_name,
        billing_cycle=billing_cycle
    )
    
    return {
        "id": subscription.id,
        "plan_name": subscription.plan_name,
        "status": subscription.status,
        "billing_cycle": subscription.billing_cycle,
        "base_price": float(subscription.base_price),
        "currency": subscription.currency,
        "updated_at": subscription.updated_at
    }


@router.post("/cancel")
def cancel_subscription(
    cancel_at_period_end: bool = True,
    reason: Optional[str] = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
    current_org: Organization = Depends(require_organization),
    member = Depends(require_manage_billing())
):
    """Cancel the current subscription."""
    
    subscription_service = SubscriptionService(session)
    
    subscription = subscription_service.cancel_subscription(
        organization_id=current_org.id,
        cancel_at_period_end=cancel_at_period_end,
        reason=reason
    )
    
    return {
        "id": subscription.id,
        "status": subscription.status,
        "cancel_at_period_end": subscription.cancel_at_period_end,
        "cancelled_at": subscription.cancelled_at,
        "cancellation_reason": subscription.cancellation_reason,
        "current_period_end": subscription.current_period_end
    }


@router.get("/invoices")
def list_invoices(
    limit: int = 20,
    offset: int = 0,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
    current_org: Organization = Depends(require_organization)
):
    """List invoices for the organization."""
    
    from sqlmodel import select
    from app.models.subscription import Invoice
    
    invoices = session.exec(
        select(Invoice)
        .where(Invoice.organization_id == current_org.id)
        .order_by(Invoice.created_at.desc())
        .offset(offset)
        .limit(limit)
    ).all()
    
    return {
        "invoices": [
            {
                "id": invoice.id,
                "invoice_number": invoice.invoice_number,
                "status": invoice.status,
                "total_amount": float(invoice.total_amount),
                "currency": invoice.currency,
                "issue_date": invoice.issue_date,
                "due_date": invoice.due_date,
                "paid_date": invoice.paid_date,
                "period_start": invoice.period_start,
                "period_end": invoice.period_end
            }
            for invoice in invoices
        ],
        "total": len(invoices),
        "limit": limit,
        "offset": offset
    }


@router.get("/invoices/{invoice_id}")
def get_invoice_details(
    invoice_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
    current_org: Organization = Depends(require_organization)
):
    """Get detailed invoice information."""
    
    from app.models.subscription import Invoice, InvoiceLineItem
    
    invoice = session.get(Invoice, invoice_id)
    if not invoice or invoice.organization_id != current_org.id:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    # Get line items
    line_items = session.exec(
        select(InvoiceLineItem).where(InvoiceLineItem.invoice_id == invoice_id)
    ).all()
    
    return {
        "id": invoice.id,
        "invoice_number": invoice.invoice_number,
        "status": invoice.status,
        "subtotal": float(invoice.subtotal),
        "tax_amount": float(invoice.tax_amount),
        "discount_amount": float(invoice.discount_amount),
        "total_amount": float(invoice.total_amount),
        "currency": invoice.currency,
        "issue_date": invoice.issue_date,
        "due_date": invoice.due_date,
        "paid_date": invoice.paid_date,
        "period_start": invoice.period_start,
        "period_end": invoice.period_end,
        "payment_method": invoice.payment_method,
        "payment_reference": invoice.payment_reference,
        "notes": invoice.notes,
        "line_items": [
            {
                "id": item.id,
                "description": item.description,
                "item_type": item.item_type,
                "quantity": item.quantity,
                "unit_price": float(item.unit_price),
                "total_price": float(item.total_price),
                "period_start": item.period_start,
                "period_end": item.period_end
            }
            for item in line_items
        ]
    }


@router.get("/analytics")
def get_subscription_analytics(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
    current_org: Organization = Depends(require_organization)
):
    """Get subscription analytics and usage trends."""
    
    subscription_service = SubscriptionService(session)
    analytics = subscription_service.get_subscription_analytics(current_org.id)
    
    return analytics


@router.post("/check-limits")
def check_operation_limits(
    operation: str,  # "create_property", "add_user", "create_booking"
    session: Session = Depends(get_session),
    current_user: User = Depends(get_active_user),
    current_org: Organization = Depends(require_organization)
):
    """Check if organization can perform a specific operation based on subscription limits."""
    
    subscription_service = SubscriptionService(session)
    
    if operation == "create_property":
        can_perform = subscription_service.can_create_property(current_org.id)
        message = "Can create property" if can_perform else "Property limit reached"
    elif operation == "add_user":
        can_perform = subscription_service.can_add_user(current_org.id)
        message = "Can add user" if can_perform else "User limit reached"
    elif operation == "create_booking":
        can_perform = subscription_service.can_create_booking(current_org.id)
        message = "Can create booking" if can_perform else "Booking limit reached"
    else:
        raise HTTPException(status_code=400, detail="Invalid operation")
    
    return {
        "operation": operation,
        "allowed": can_perform,
        "message": message,
        "usage": subscription_service.check_usage_limits(current_org.id)
    }
