from abc import ABC, abstractmethod

from selene.domains.market_data.value_objects.api_response import APIResponse


class MarketDataAPIPort(ABC):
    """Port for market data API operations"""

    @abstractmethod
    def get_market_data(self, symbol: str) -> APIResponse:
        """Fetch market data for a given symbol."""

    @abstractmethod
    def get_bulk_market_data(self, symbols: list[str]) -> APIResponse:
        """Fetch market data for multiple symbols."""
