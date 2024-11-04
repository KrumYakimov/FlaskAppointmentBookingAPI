from datetime import datetime

from sqlalchemy import Integer, ForeignKey, String, DateTime, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db import db
from models import UserModel, ServiceModel
from models.emums import AppointmentState
from utils.mixins import TimestampMixin


class AppointmentModel(db.Model, TimestampMixin):
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    service_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("services.id"), nullable=False
    )
    staff_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    customer_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    appointment_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=AppointmentState.PENDING.value
    )

    # Relationships using string-based foreign keys
    service = relationship(
        "ServiceModel", back_populates="appointments"
    )
    staff = relationship(
        "UserModel",
        foreign_keys="AppointmentModel.staff_id",
        back_populates="staff_appointments",
    )
    customer = relationship(
        "UserModel",
        foreign_keys="AppointmentModel.customer_id",
        back_populates="customer_appointments",
    )


def __repr__(self):
    return (f"<Appointment(id={self.id}, service_id={self.service_id}, "
            f"staff_id={self.staff_id}, customer_id={self.customer_id}, "
            f"appointment_time={self.appointment_time}, status={self.status})>")
