from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AuctionConfig(BaseSettings):
    """Auction business rules and background task intervals."""

    lot_duration_minutes: int = Field(default=5, description="Initial lot duration when created")
    extend_minutes: int = Field(default=1, description="Extension per bid")
    close_lots_interval_sec: int = Field(default=30, description="Background task: check expired lots every N seconds")

    model_config = SettingsConfigDict(env_prefix="AUCTION_", extra="ignore")
