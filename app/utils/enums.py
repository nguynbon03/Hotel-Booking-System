from enum import Enum

# -----------------------------
# USER ROLE (CHỈ CÁI NÀY PHẢI DÙNG ENUM)
# -----------------------------
class UserRole(str, Enum):
    CUSTOMER = "CUSTOMER"
    ADMIN = "ADMIN"
    STAFF = "STAFF"


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
