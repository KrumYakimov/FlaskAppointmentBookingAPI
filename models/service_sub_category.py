from sqlalchemy.orm import Mapped, mapped_column, relationship

from db import db
from models import ServiceModel


class ServiceSubcategoryModel(db.Model):
    __tablename__ = "subcategories"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(db.String(100), nullable=False, unique=True)

    # Foreign key to link the subcategory to a category
    category_id: Mapped[int] = mapped_column(
        db.Integer,
        db.ForeignKey(
            'categories.id',
            name="fk_subcategories_categories"
        ),
        nullable=False
    )

    # Relationship back to category
    category = relationship(
        "ServiceCategoryModel",
        back_populates="service_subcategories",
        lazy="select"
    )

    # Relationship back to service
    services = relationship(
        "ServiceModel",
        back_populates="service_subcategory",
        lazy="select"
    )

