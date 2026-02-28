"""WebSocket message types and payloads for lot events."""

import enum
from typing import TypedDict


class WsMessageType(str, enum.Enum):
    """Type of WebSocket message sent to lot subscribers."""

    new_bid = "new_bid"
    time_extended = "time_extended"
    lot_ended = "lot_ended"


class NewBidPayload(TypedDict):
    type: str
    amount: str
    bidder_name: str
    created_at: str


class TimeExtendedPayload(TypedDict):
    type: str
    end_time: str


class LotEndedPayload(TypedDict):
    type: str
    status: str
