class UserRole:
    CUSTOMER = "customer"
    ADMIN = "admin"
    STAFF = "staff"

class BookingStatus:
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

class PaymentStatus:
    INIT = "init"
    SUCCESS = "success"
    FAILED = "failed"

class PaymentMethod:
    CARD = "card"
    BANK = "bank"
    COD = "cod"
