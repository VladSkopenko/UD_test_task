from datetime import datetime, timezone
from fastapi import WebSocket
from typing import Dict, Set, Union

from src.app.features.auction.models.lot import LotStatus
from src.app.infrastructure.websocket.types import (
    LotEndedPayload,
    NewBidPayload,
    TimeExtendedPayload,
    WsMessageType,
)

import logging

logger = logging.getLogger(__name__)


class LotWebSocketManager:
    """Manages WebSocket connections per lot. Broadcasts events to subscribers of a lot."""

    def __init__(self):
        self._connections: Dict[int, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, lot_id: int) -> None:
        await websocket.accept()
        if lot_id not in self._connections:
            self._connections[lot_id] = set()
        self._connections[lot_id].add(websocket)

    def disconnect(self, websocket: WebSocket, lot_id: int) -> None:
        if lot_id in self._connections:
            self._connections[lot_id].discard(websocket)
            if not self._connections[lot_id]:
                del self._connections[lot_id]

    async def broadcast_bid(
        self,
        lot_id: int,
        *,
        amount: str,
        bidder_name: str,
    ) -> None:
        payload: NewBidPayload = {
            "type": WsMessageType.new_bid.value,
            "amount": amount,
            "bidder_name": bidder_name,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        await self._broadcast(lot_id, payload)

    async def broadcast_time_extended(self, lot_id: int, end_time: datetime) -> None:
        payload: TimeExtendedPayload = {
            "type": WsMessageType.time_extended.value,
            "end_time": end_time.isoformat(),
        }
        await self._broadcast(lot_id, payload)


    async def broadcast_lot_ended(self, lot_id: int) -> None:
        payload: LotEndedPayload = {
            "type": WsMessageType.lot_ended.value,
            "status": LotStatus.ended.value,
        }
        await self._broadcast(lot_id, payload)

    async def _broadcast(
        self,
        lot_id: int,
        payload: Union[NewBidPayload, TimeExtendedPayload, LotEndedPayload],
    ) -> None:
        if lot_id not in self._connections:
            return
        dead = set()
        for ws in self._connections[lot_id]:
            try:
                await ws.send_json(payload)
            except Exception:
                dead.add(ws)
        for ws in dead:
            self._connections[lot_id].discard(ws)
        if not self._connections[lot_id]:
            del self._connections[lot_id]


ws_lot_manager = LotWebSocketManager()
