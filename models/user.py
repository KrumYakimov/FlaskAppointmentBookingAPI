from sqlalchemy.orm import Mapped, mapped_column, relationship

from db import db
from models.emums import RoleType
from models.junctions import owner_service_provider_association
from utils.mixins import PersonalInfoMixin, TimestampMixin


class UserModel(db.Model, PersonalInfoMixin, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    password: Mapped[str] = mapped_column(db.String(255), nullable=False)
    role: Mapped[RoleType] = mapped_column(
        db.Enum(RoleType),
        default=RoleType.CLIENT.name,
        nullable=False
    )
    is_active: Mapped[bool] = mapped_column(default=True)  # Soft delete flag

    # One-to-Many relationship to service provider for staff
    service_provider_id: Mapped[int] = mapped_column(
        db.Integer,
        db.ForeignKey(
            'service_providers.id',
            name="fk_users_service_provider",
        ),
        nullable=True
    )

    # Many-to-Many relationship to service providers for owners
    owned_companies = relationship(
        "ServiceProviderModel",
        secondary=owner_service_provider_association,
        back_populates="owners",
        lazy="select"
    )

    # Relationship with the ServiceProviderModel
    service_provider = relationship(
        "ServiceProviderModel",
        back_populates="employees",
        lazy="select",
    )

    # Relationship with the ServiceModel (if the staff handles multiple services)
    services = relationship(
        "ServiceModel",
        back_populates="staff",
        lazy="select"
    )

    # Soft delete check for queries
    @staticmethod
    def query_active():
        return UserModel.query.filter_by(is_active=True)

