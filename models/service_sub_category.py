from sqlalchemy.orm import Mapped, mapped_column, relationship

from db import db
from utils.mixins import TimestampMixin


class ServiceSubcategoryModel(db.Model, TimestampMixin):

    __tablename__ = "subcategories"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(db.String(100), nullable=False, unique=True)
    is_active: Mapped[bool] = mapped_column(default=True)

    # Foreign key to link the subcategory to a category
    category_id: Mapped[int] = mapped_column(
        db.Integer,
        db.ForeignKey("categories.id", name="fk_subcategories_categories"),
        nullable=False,
    )

    # Relationship back to ServiceCategoryModel
    service_category = relationship(
        "ServiceCategoryModel", back_populates="service_subcategories", lazy="select"
    )

    # Relationship back to service
    services = relationship(
        "ServiceModel", back_populates="service_subcategory", lazy="select"
    )
