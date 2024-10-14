from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db import db
from models.emums import RoleType
from models.junctions import owner_service_provider_association
from utils.mixins import PersonalInfoMixin, TimestampMixin


class UserModel(db.Model, PersonalInfoMixin, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    role: Mapped[RoleType] = mapped_column(
        db.Enum(RoleType),
        default=RoleType.CLIENT.name,
        nullable=False
    )

    # Many-to-Many relationship to service providers for owners
    owned_companies = db.relationship(
        "ServiceProviderModel",
        secondary=owner_service_provider_association,
        back_populates="owners"
    )

    # One-to-Many relationship to service provider for staff
    service_provider_id: Mapped[int] = mapped_column(
        db.Integer, db.ForeignKey('service_providers.id'),
        nullable=True
    )

    # Relationship with the ServiceProviderModel
    service_provider = relationship(
        "ServiceProviderModel",
        back_populates="employees",
        lazy=True,
        foreign_keys='UserModel.service_provider_id'
    )

