from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db import db
from models.emums import RoleType
from utils.mixins import PersonalInfoMixin, TimestampMixin


class UserModel(db.Model, PersonalInfoMixin, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    password: Mapped[str] = mapped_column(db.String(255), nullable=False)


