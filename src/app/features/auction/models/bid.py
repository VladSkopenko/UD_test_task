from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey, text, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.common.base import Base


class Bid(Base):
    __tablename__ = "bids"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    lot_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("lots.id", ondelete="CASCADE"),
        nullable=False,
    )
    amount: Mapped[str] = mapped_column(String(50), nullable=False)
    bidder_name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    lot: Mapped["Lot"] = relationship("Lot", back_populates="bids")
