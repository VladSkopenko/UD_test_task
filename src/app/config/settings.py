from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.app.config.auction_config import AuctionConfig


class Settings(BaseSettings):
    DATABASE_URL: str
    auction: AuctionConfig = Field(default_factory=AuctionConfig)

    model_config = SettingsConfigDict(
        env_file=("public_env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
