from datetime import datetime

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.features.auction.models import Lot
from src.app.features.auction.models.lot import LotStatus


class LotRepository:
    """Repository for Lot entity. All DB access for lots."""

    async def create(self, db: AsyncSession, lot: Lot) -> Lot:
        db.add(lot)
        await db.flush()
        await db.refresh(lot)
        return lot

    async def get_by_id(self, db: AsyncSession, lot_id: int) -> Lot | None:
        result = await db.execute(select(Lot).where(Lot.id == lot_id))
        return result.scalar_one_or_none()

    async def get_by_id_for_update(self, db: AsyncSession, lot_id: int) -> Lot | None:
        result = await db.execute(
            select(Lot).where(Lot.id == lot_id).with_for_update()
        )
        return result.scalar_one_or_none()

    async def list_active(self, db: AsyncSession, now: datetime) -> list[Lot]:
        result = await db.execute(
            select(Lot)
            .where(
                and_(
                    Lot.status == LotStatus.running,
                    Lot.end_time > now,
                )
            )
            .order_by(Lot.created_at.desc())
        )
        return list(result.scalars().all())

    async def close_expired(self, db: AsyncSession, now: datetime) -> list[Lot]:
        result = await db.execute(
            select(Lot).where(
                and_(
                    Lot.status == LotStatus.running,
                    Lot.end_time < now,
                )
            )
        )
        lots = result.scalars().all()
        for lot in lots:
            lot.status = LotStatus.ended
        await db.flush()
        return list(lots)


def get_lot_repository() -> LotRepository:
    """Factory for LotRepository dependency injection."""
    return LotRepository()
