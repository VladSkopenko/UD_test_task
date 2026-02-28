from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from src.app.features.auction.models.enums import LotStatus


class LotCreate(BaseModel):
    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Lot title",
        examples=["iPhone 15 Pro 256GB"],
    )
    starting_price: float = Field(
        ...,
        gt=0,
        description="Starting price of the lot, must be greater than 0",
        examples=[99.99],
    )


class LotResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    starting_price: str
    status: str
    end_time: datetime
    created_at: datetime


class LotListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    starting_price: str
    status: LotStatus
    end_time: datetime
