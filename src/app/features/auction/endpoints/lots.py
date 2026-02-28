from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.common.database import get_db
from src.app.features.auction.schemas.lot import LotCreate, LotResponse, LotListResponse
from src.app.features.auction.services.lot_service import LotServiceDep

router = APIRouter()


@router.post("", response_model=LotResponse)
async def create_lot(
    data: LotCreate,
    service: LotServiceDep,
    db: AsyncSession = Depends(get_db),
) -> LotResponse:
    lot = await service.create_lot(db=db, data=data)
    return LotResponse.model_validate(lot)


@router.get("", response_model=list[LotListResponse])
async def list_lots(
    service: LotServiceDep,
    db: AsyncSession = Depends(get_db),
):
    lots = await service.list_lots(db)
    return [LotListResponse.model_validate(lot) for lot in lots]
