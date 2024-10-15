from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, declarative_mixin

from db import db


@declarative_mixin
class PersonalInfoMixin:
    email: Mapped[str] = mapped_column(db.String(50), nullable=False, unique=True)
    first_name: Mapped[str] = mapped_column(db.String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(db.String(50), nullable=False)
    phone: Mapped[str] = mapped_column(db.String(20), unique=True)


@declarative_mixin
class TimestampMixin:
    created_on: Mapped[datetime] = mapped_column(
        server_default=func.timezone('UTC', func.now()),
        nullable=False
    )
    updated_on: Mapped[datetime] = mapped_column(
        onupdate=func.timezone('UTC', func.now()),
        server_default=func.timezone('UTC', func.now()),
        nullable=False
    )


@declarative_mixin
class AddressMixin:
    country: Mapped[str] = mapped_column(db.String(2), nullable=False)  # ISO code A-2
    district: Mapped[str] = mapped_column(db.String(50), nullable=True)
    city: Mapped[str] = mapped_column(db.String(50), nullable=False)
    neighborhood: Mapped[str] = mapped_column(db.String(50), nullable=True)
    street: Mapped[str] = mapped_column(db.String(50), nullable=False)
    street_number: Mapped[str] = mapped_column(db.String(15), nullable=False)
    block_number: Mapped[str] = mapped_column(db.String(15), nullable=True)
    apartment: Mapped[str] = mapped_column(db.String(15), nullable=True)
    floor: Mapped[str] = mapped_column(db.String(10), nullable=True)
    postal_code: Mapped[str] = mapped_column(db.String(20), nullable=False)
    latitude: Mapped[float] = mapped_column(nullable=True)
    longitude: Mapped[float] = mapped_column(nullable=True)
