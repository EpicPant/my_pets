"""make db session file"""

from datetime import datetime
from typing import Any, Dict, Annotated
from sqlalchemy import TIMESTAMP, func, Integer
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncAttrs,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr
from app.core.config import db_settings

engine = create_async_engine(
    url=db_settings.DB_URL,
    echo=True,
    pool_size=5,
    max_overflow=10,
    pool_timeout=60,
    pool_pre_ping=True,
)

async_session = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

str_uniq = Annotated[str, mapped_column(unique=True, nullable=False)]


class Base(AsyncAttrs, DeclarativeBase):
    """Base class for orm models"""

    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.now()  # pylint: disable=E1102
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.now()  # pylint: disable=E1102
    )

    @declared_attr.directive
    def __tablename__(cls) -> str:  # pylint: disable=no-self-argument
        return cls.__name__.lower() + "s"

    def to_dict(self) -> Dict[str, Any]:
        """get dict from ORM-model"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return f"<{self.__class__.__name__}>: (id={self.id}, created_at={self.created_at}, updated_at={self.updated_at})"
