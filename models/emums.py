import enum


class RoleType(enum.Enum):
    ADMIN = "admin"
    CLIENT = "client"
    OWNER = "company_representative"
    STAFF = "staff"


class AppointmentState(enum.Enum):
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    NO_SHOW = "no_show"
    PENDING = "pending"


class ProviderRegistrationState(enum.Enum):
    APPROVED = "approved"
    PENDING = "pending"
    REJECTED = "rejected"
    NO_SHOW = "no_show"


class ServiceCategory(enum.Enum):
    MANICURE = "manicure"
    EYEBROWS = "eyebrows"
    EYELASHES = "eyelashes"
    HAIR = "hair"
    FACE = "face"
    MASSAGE = "massage"
    WAXING = "waxing"
    MAKEUP = "makeup"
    LASER_HAIR_REMOVAL = "laser_hair_removal"
    BEARD = "beard"


