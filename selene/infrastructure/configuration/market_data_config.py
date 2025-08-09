from dataclasses import dataclass

from selene.infrastructure.database.db_config import DatabaseConnectionConfig


@dataclass
class APIConfig:
    """Typed configuration for API settings"""

    base_url: str
    api_key: str  # Will be loaded from environment
    timeout_seconds: int = 30
    retry_attempts: int = 3
    rate_limit_per_minute: int = 60

    def __post_init__(self) -> None:
        # Validate required fields
        if not self.base_url:
            raise ValueError("API base_url is required")
        if not self.api_key:
            raise ValueError("API key is required")
        if not self.base_url.startswith(("http://", "https://")):
            raise ValueError("API base_url must be a valid URL")


@dataclass
class MarketDataConfig:
    """Main configuration container for market data application."""

    api: APIConfig
    database: DatabaseConnectionConfig
