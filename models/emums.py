import enum


class RoleType(enum.Enum):
    ADMIN = "admin"
    SERVICE_PROVIDER = "service_provider"
    CLIENT = "client"


class AppointmentStateType(enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    NO_SHOW = "no_show"
