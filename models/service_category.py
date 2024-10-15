from sqlalchemy.orm import Mapped, mapped_column, relationship

from db import db


class ServiceCategoryModel(db.Model):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(db.String(100), nullable=False, unique=True)

    # Relationship to subcategories
    subcategories = relationship(
        "ServiceSubcategoryModel",
        back_populates="service_category",
        lazy="select"
    )
