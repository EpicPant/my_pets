"""Models and DAO for payments and wallets"""

import uuid
from decimal import Decimal
from typing import TYPE_CHECKING
from sqlalchemy import Numeric, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.base.database import Base
from app.base.BaseDAO import BaseDAO

if TYPE_CHECKING:
    from app.models.user import User


class Wallet(Base):
    """Wallet model"""

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="wallet", uselist=False)
    balance: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, server_default="0"
    )
    transactions = relationship("Transaction", back_populates="wallet")


class Transaction(Base):
    """Transaction model"""

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True)
    wallet_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("wallets.id"))
    operation_type: Mapped[str] = mapped_column(String, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    balance_before: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    balance_after: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    wallet = relationship("Wallet", back_populates="transactions")


class WalletDAO(BaseDAO):
    """DAO class for wallet model"""

    model = Wallet


class TransactionDAO(BaseDAO):
    """DAO class for transactions"""

    model = Transaction
