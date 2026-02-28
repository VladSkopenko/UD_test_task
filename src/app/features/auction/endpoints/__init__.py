from fastapi import APIRouter

from src.app.features.auction.endpoints.lots import router as lots_router
from src.app.features.auction.endpoints.bids import router as bids_router
from src.app.features.auction.endpoints.websocket import router as ws_router

router = APIRouter()
router.include_router(lots_router, prefix="/lots", tags=["lots"])
router.include_router(
    bids_router, prefix="/lots/{lot_id}/bids", tags=["bids"]
)
router.include_router(ws_router, tags=["WebSocket"])
