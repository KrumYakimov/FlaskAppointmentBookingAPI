from sqlalchemy.orm import Mapped, mapped_column

from db import db
from models.emums import ProviderRegistrationState
from utils.mixins import PersonalInfoMixin, AddressMixin


class InquiryModel(db.Model, PersonalInfoMixin):
    __tablename__ = "inquiries"

    id: Mapped[int] = mapped_column(primary_key=True)
    salon_name: Mapped[str] = mapped_column(db.String(100), nullable=False)
    city: Mapped[str] = mapped_column(db.String(50), nullable=False)
    status: Mapped[ProviderRegistrationState] = mapped_column(
        db.Enum(ProviderRegistrationState),
        nullable=False,
        default=ProviderRegistrationState.PENDING
    )

