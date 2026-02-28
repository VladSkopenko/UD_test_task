from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.common.database import get_db
from src.app.features.auction.schemas.bid import BidCreate, BidResponse
from src.app.features.auction.services.lot_service import LotServiceDep

router = APIRouter()


@router.post("", response_model=BidResponse)
async def place_bid(
    lot_id: int,
    data: BidCreate,
    service: LotServiceDep,
    db: AsyncSession = Depends(get_db),
):
    bid = await service.place_bid(db, lot_id, data)
    return BidResponse.model_validate(bid)

