from enum import Enum

# -----------------------------
# USER ROLE (CHỈ CÁI NÀY PHẢI DÙNG ENUM)
# -----------------------------
class UserRole(str, Enum):
    CUSTOMER = "CUSTOMER"
    ADMIN = "ADMIN"
    STAFF = "STAFF"


# -----------------------------
# ORGANIZATION ROLE (MULTI-TENANCY)
# -----------------------------
class OrganizationRole(str, Enum):
    """Roles within an organization for multi-tenancy."""
    OWNER = "OWNER"           # Full control, billing access
    ADMIN = "ADMIN"           # Full operational control, no billing
    MANAGER = "MANAGER"       # Property and booking management
    STAFF = "STAFF"           # Basic booking operations
    MEMBER = "MEMBER"         # Read-only access


# -----------------------------
# Booking Status (KHÔNG ĐỤNG TỚI)
# -----------------------------
class BookingStatus:
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


# -----------------------------
# Payment Status (KHÔNG ĐỤNG TỚI)
# -----------------------------
class PaymentStatus:
    INIT = "init"
    SUCCESS = "success"
    FAILED = "failed"


# -----------------------------
# Payment Method (KHÔNG ĐỤNG TỚI)
# -----------------------------
class PaymentMethod:
    CARD = "card"
    BANK = "bank"
    COD = "cod"
