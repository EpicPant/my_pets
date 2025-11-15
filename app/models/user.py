"""User model and DAO"""

import uuid
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.base.database import Base, str_uniq
from app.base.BaseDAO import BaseDAO

if TYPE_CHECKING:
    from app.models.payments import Wallet


class User(Base):
    """User model"""

    name: Mapped[str]
    email: Mapped[str_uniq]
    password: Mapped[str] = mapped_column(nullable=False)
    wallet: Mapped["Wallet | None"] = relationship(back_populates="user")


class UserDAO(BaseDAO):
    """UserDAO class"""

    model = User
