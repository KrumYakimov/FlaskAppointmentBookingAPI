import enum


class RoleType(enum.Enum):
    ADMIN = "admin"
    APPROVER = "approver"
    CLIENT = "client "
    OWNER = "company_representative"
    STAFF = "staff"


class AppointmentState(enum.Enum):
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    NO_SHOW = "no_show"
    REJECTED = "rejected"
    PENDING = "pending"


class ProviderRegistrationState(enum.Enum):
    APPROVED = "approved"
    PENDING = "pending"
    REJECTED = "rejected"
    NO_SHOW = "no_show"


# class PaymentMethod(enum.Enum):
#     CASH = "cash"
#     DEBIT_CARD = "debit_card"
#     CREDIT_CARD = "credit_card"
#
#
# class PaymentStatus(enum.Enum):
#     PENDING = "pending"
#     HELD = "held"
#     COMPLETED = "completed"
#     CANCELED = "canceled"

