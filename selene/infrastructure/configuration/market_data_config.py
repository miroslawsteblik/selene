from dataclasses import dataclass, field

from selene.infrastructure.database.db_config import DatabaseConnectionConfig


@dataclass
class APIConfig:
    """Typed configuration for API settings"""

    base_url: str
    params: dict = field(default_factory=dict)
    timeout_seconds: int = 30
    retry_attempts: int = 3
    rate_limit_per_minute: int = 60
    symbols: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.base_url:
            raise ValueError("API base_url is required")
        if not self.base_url.startswith(("http://", "https://")):
            raise ValueError("API base_url must be a valid URL")
        if not self.symbols:
            raise ValueError("API symbols list cannot be empty")


@dataclass
class MarketDataConfig:
    """Main configuration container for market data application."""

    api: APIConfig
    database: DatabaseConnectionConfig
    schema: dict = field(default_factory=dict)
