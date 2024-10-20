from sqlalchemy.orm import Mapped, mapped_column, relationship

from db import db
from models import owner_service_provider_association
from utils.mixins import AddressMixin


class ServiceProviderModel(db.Model, AddressMixin):
    __tablename__ = "service_providers"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    company_name: Mapped[str] = mapped_column(db.String(100), nullable=False)
    trade_name: Mapped[str] = mapped_column(db.String(100), nullable=False)
    uic: Mapped[str] = mapped_column(db.String(20), unique=True, nullable=False)

    # Many-to-One Relationship to InquiryModel
    inquiry_id: Mapped[int] = mapped_column(
        db.Integer,
        db.ForeignKey(
            'inquiries.id',
            name="fk_service_providers_inquiries"
        ),
        nullable=True
    )
    # Relationship to link to InquiryModel
    inquiry = relationship(
        "InquiryModel",
        back_populates="service_provider",
        lazy="select"
    )

    # Relationship to link with employees (staff) via the UserModel
    employees = relationship(
        "UserModel",
        back_populates="service_provider",
        lazy="select"
    )

    # Relationship with services offered by this provider
    services = relationship(
        "ServiceModel",
        back_populates="service_provider",
        lazy="select"
    )

    # Many-to-Many Relationship to match the owned_companies in UserModel
    owners = relationship(
        "UserModel",
        secondary=owner_service_provider_association,
        back_populates="owned_companies"
    )

