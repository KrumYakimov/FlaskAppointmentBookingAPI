from datetime import time

from sqlalchemy.orm import Mapped, mapped_column, relationship

from db import db


class WorkingHoursModel(db.Model):
    __tablename__ = "working_hours"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    day_of_week: Mapped[int] = mapped_column(
        db.Integer, nullable=False
    )  # 0 = Monday, 6 = Sunday
    start_time: Mapped[time] = mapped_column(db.Time, nullable=False)
    end_time: Mapped[time] = mapped_column(db.Time, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)

    # Foreign key linking to the ServiceProvider and UserModel (staff)
    provider_id: Mapped[int] = mapped_column(
        db.Integer, db.ForeignKey("service_providers.id"), nullable=False
    )
    employee_id: Mapped[int] = mapped_column(
        db.Integer, db.ForeignKey("users.id"), nullable=False
    )

    # Relationships
    provider = relationship("ServiceProviderModel", back_populates="working_hours")
    employee = relationship("UserModel", back_populates="working_hours")
