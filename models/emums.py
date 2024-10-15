import enum


class RoleType(enum.Enum):
    ADMIN = "admin"
    APPROVER = "approver"
    CLIENT = "client"
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


