from enum import Enum


class UserRole(str, Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    ADMIN = "ADMIN"        # admin_org
    STAFF = "STAFF"        # staff của property
    CUSTOMER = "CUSTOMER"  # khách đặt phòng


class LocationType(str, Enum):
    COUNTRY = "country"
    PROVINCE = "province"
    CITY = "city"
    DISTRICT = "district"


class BookingStatus(str, Enum):
    PENDING = "PENDING"
    HOLD = "HOLD"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"


class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"


class PropertyType(str, Enum):
    HOTEL = "HOTEL"
    APARTMENT = "APARTMENT"
    HOSTEL = "HOSTEL"
    VILLA = "VILLA"


class SubscriptionPlan(str, Enum):
    FREE = "FREE"
    BASIC = "BASIC"
    PROFESSIONAL = "PROFESSIONAL"
    ENTERPRISE = "ENTERPRISE"


class SubscriptionStatus(str, Enum):
    TRIALING = "TRIALING"
    ACTIVE = "ACTIVE"
    PAST_DUE = "PAST_DUE"
    CANCELED = "CANCELED"
    INACTIVE = "INACTIVE"


class BillingCycle(str, Enum):
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"


class InvoiceStatus(str, Enum):
    DRAFT = "DRAFT"
    OPEN = "OPEN"
    PAID = "PAID"
    VOID = "VOID"
    OVERDUE = "OVERDUE"


class InvitationStatus(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"
    EXPIRED = "EXPIRED"


class ReviewStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


# Bạn bị thiếu cái này, mà Organization đang dùng → PHẢI có
class OrganizationStatus(str, Enum):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    TRIAL = "TRIAL"
    EXPIRED = "EXPIRED"
