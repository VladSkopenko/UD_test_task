import asyncio
import logging

from src.app.common.database import get_db
from src.app.config.settings import settings
from src.app.features.auction.services.lot_service import LotService
from src.app.infrastructure.websocket.manager import ws_lot_manager

logger = logging.getLogger(__name__)


async def close_expired_lots_task() -> None:
    """Background task: close lots with end_time < now and broadcast lot_ended via WebSocket."""
    interval_sec = settings.auction.close_lots_interval_sec
    service = LotService()
    while True:
        try:
            async for db in get_db():
                try:
                    closed = await service.close_expired_lots(db)
                    await db.commit()
                    for lot in closed:
                        await ws_lot_manager.broadcast_lot_ended(lot.id)
                        logger.info("Lot ended", extra={"lot_id": lot.id})
                except Exception:
                    await db.rollback()
                    raise
                break
        except Exception:
            logger.exception("Error in close_expired_lots_task")
        await asyncio.sleep(interval_sec)
