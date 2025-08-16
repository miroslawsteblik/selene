from abc import ABC, abstractmethod
from typing import List, Optional

from selene.domains.market_data.entities.market_data import MarketData


class MarketDataRepositoryPort(ABC):
    """Port for market data persistence."""
    @abstractmethod
    def save(self, market_data: MarketData) -> MarketData:
        """Save market data to the repository."""

    @abstractmethod
    def update(self, market_data: MarketData) -> MarketData:
        """Update existing market data in the repository."""

    @abstractmethod
    def find_by_symbol(self, symbol: str) -> Optional[MarketData]:
        """Find market data by symbol."""

    @abstractmethod
    def find_all_recent(self, hours: int = 24) -> List[MarketData]:
        """Find all market data entries created within the last 'hours' hours."""
