from __future__ import annotations

from datetime import datetime

from sqlalchemy import String, DateTime, Enum as SQLEnum, text, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.common.base import Base
from src.app.features.auction.models.enums import LotStatus


class Lot(Base):
    __tablename__ = "lots"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    starting_price: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[LotStatus] = mapped_column(
        SQLEnum(LotStatus), nullable=False, default=LotStatus.running
    )
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    bids: Mapped[list["Bid"]] = relationship(
        "Bid", back_populates="lot", order_by="Bid.created_at"
    )
