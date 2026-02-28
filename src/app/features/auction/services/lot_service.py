from datetime import datetime, timedelta
from decimal import Decimal
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.common.datetime_utils import DateTimeUtils
from src.app.common.decorators import handle_errors
from src.app.config.settings import settings
from src.app.features.auction.models import Lot, Bid
from src.app.features.auction.models.lot import LotStatus
from src.app.features.auction.repositories.lot_repository import (
    LotRepository,
    get_lot_repository,
)
from src.app.features.auction.repositories.bid_repository import (
    BidRepository,
    get_bid_repository,
)
from src.app.features.auction.schemas.lot import LotCreate
from src.app.features.auction.schemas.bid import BidCreate
from src.app.infrastructure.websocket.manager import ws_lot_manager


class LotService:
    """Business logic for lots and bids. No DB access; uses repositories."""

    def __init__(
        self,
        lot_repo: LotRepository | None = None,
        bid_repo: BidRepository | None = None,
    ) -> None:
        self._lot_repo = lot_repo or LotRepository()
        self._bid_repo = bid_repo or BidRepository()
        self._config = settings.auction

    @staticmethod
    def _to_decimal(value: float | str) -> Decimal:
        return Decimal(str(value))

    def _resolve_end_time(self) -> datetime:
        return DateTimeUtils.utc_now() + timedelta(minutes=self._config.lot_duration_minutes)

    def _format_price(self, price: float) -> str:
        return str(self._to_decimal(price).quantize(Decimal("0.01")))

    @staticmethod
    def _validate_lot_active(lot: Lot | None) -> Lot:
        if not lot:
            raise ValueError("Lot not found")
        if lot.status != LotStatus.running:
            raise ValueError("Lot is not running")
        if DateTimeUtils.utc_now() >= lot.end_time:
            raise ValueError("Lot has already ended")
        return lot

    @handle_errors
    async def create_lot(self, db: AsyncSession, data: LotCreate) -> Lot:
        lot = Lot(
            title=data.title,
            starting_price=self._format_price(data.starting_price),
            status=LotStatus.running,
            end_time=self._resolve_end_time(),
        )
        return await self._lot_repo.create(db, lot)

    @handle_errors
    async def place_bid(self, db: AsyncSession, lot_id: int, data: BidCreate) -> Bid:
        lot = self._validate_lot_active(
            await self._lot_repo.get_by_id_for_update(db, lot_id)
        )

        amount_str = str(self._to_decimal(data.amount).quantize(Decimal("0.01")))
        bid = Bid(
            lot_id=lot_id,
            amount=amount_str,
            bidder_name=data.bidder_name,
        )
        await self._bid_repo.create(db, bid)

        new_end = max(lot.end_time, DateTimeUtils.utc_now()) + timedelta(minutes=self._config.extend_minutes)
        lot.end_time = new_end
        await db.flush()

        await ws_lot_manager.broadcast_bid(
            lot_id,
            amount=bid.amount,
            bidder_name=data.bidder_name,
        )
        await ws_lot_manager.broadcast_time_extended(lot_id, new_end)

        return bid

    @handle_errors
    async def list_lots(self, db: AsyncSession) -> list[Lot]:
        return await self._lot_repo.list_active(db, DateTimeUtils.utc_now())

    @handle_errors
    async def close_expired_lots(self, db: AsyncSession) -> list[Lot]:
        return await self._lot_repo.close_expired(db, DateTimeUtils.utc_now())


def get_lot_service(
    lot_repo: LotRepository = Depends(get_lot_repository),
    bid_repo: BidRepository = Depends(get_bid_repository),
) -> LotService:
    """Factory for LotService dependency injection."""
    return LotService(lot_repo=lot_repo, bid_repo=bid_repo)


LotServiceDep = Annotated[LotService, Depends(get_lot_service)]
