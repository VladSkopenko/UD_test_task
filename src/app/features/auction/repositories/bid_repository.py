from sqlalchemy.ext.asyncio import AsyncSession

from src.app.features.auction.models import Bid


class BidRepository:
    """Repository for Bid entity. All DB access for bids."""

    async def create(self, db: AsyncSession, bid: Bid) -> Bid:
        db.add(bid)
        await db.flush()
        await db.refresh(bid)
        return bid


def get_bid_repository() -> BidRepository:
    """Factory for BidRepository dependency injection."""
    return BidRepository()
