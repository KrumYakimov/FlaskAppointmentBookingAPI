from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db import db
from models.emums import RoleType


class UserModel(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(db.String(50), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(db.String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(db.String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(db.String(50), nullable=False)
    phone: Mapped[str] = mapped_column(db.String(20), unique=True)
    role: Mapped[RoleType] = mapped_column(db.Enum(RoleType), default=RoleType.CLIENT.name, nullable=False)
    created_on = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_on = db.Column(db.DateTime(timezone=True), onupdate=func.now())