from sqlalchemy.orm import Mapped, mapped_column, relationship

from db import db
from utils.mixins import TimestampMixin


class ServiceCategoryModel(db.Model, TimestampMixin):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(db.String(100), nullable=False, unique=True)
    is_active: Mapped[bool] = mapped_column(default=True)  # Soft delete flag

    # Relationship to ServiceSubcategoriesModel
    service_subcategories = relationship(
        "ServiceSubcategoryModel", back_populates="service_category", lazy="select"
    )
