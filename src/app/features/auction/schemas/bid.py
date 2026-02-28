from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class BidCreate(BaseModel):
    bidder_name: str = Field(..., min_length=1, max_length=255, description="Display name of the bidder", examples=["Alice"])
    amount: float = Field(..., gt=0, description="Bid amount, must be greater than 0", examples=[110.00])


class BidResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    amount: str
    bidder_name: str
    created_at: datetime
