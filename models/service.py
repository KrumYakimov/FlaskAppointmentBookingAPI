from sqlalchemy.orm import Mapped, mapped_column, relationship

from db import db
from utils.mixins import TimestampMixin


class ServiceModel(db.Model, TimestampMixin):
    __tablename__ = "services"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(50), nullable=False)
    price: Mapped[float] = mapped_column(db.Numeric(10, 2), nullable=False)

    # Foreign key linking to the service subcategory
    service_subcategory_id: Mapped[int] = mapped_column(
        db.Integer,
        db.ForeignKey("subcategories.id", name="fk_services_subcategories"),
        nullable=False,
    )

    # Foreign key linking to the service provider offering this service
    service_provider_id = mapped_column(
        db.Integer,
        db.ForeignKey("service_providers.id", name="fk_services_service_providers"),
        nullable=False,
    )

    # Foreign key to link the staff member (employee) responsible for the service
    staff_id: Mapped[int] = mapped_column(
        db.Integer, db.ForeignKey("users.id", name="fk_services_users"), nullable=True
    )

    # Relationship with the ServiceSubcategoryModel
    service_subcategory = relationship(
        "ServiceSubcategoryModel", back_populates="services", lazy="select"
    )

    # Relationship with the ServiceProviderModel, linking the service to the beauty salon providing it
    service_provider = relationship(
        "ServiceProviderModel", back_populates="services", lazy="select"
    )

    # Relationship with UserModel (staff member responsible for the service)
    staff = relationship("UserModel", back_populates="services", lazy="select")
