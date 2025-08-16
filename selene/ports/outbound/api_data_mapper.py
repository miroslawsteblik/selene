from abc import ABC, abstractmethod
from typing import Any, Dict, List

from selene.domains.market_data.entities.market_data import MarketData


class DataMapperPort(ABC):
    """Port for mapping API data to domain entities."""

    @abstractmethod
    def map_to_market_data(self, api_data: Dict[str, Any], symbol: str) -> MarketData:
        """Map API data to MarketData entity."""

    @abstractmethod
    def validate_api_schema(self, api_data: Dict[str, Any]) -> List[str]:
        """Validate the structure of the API data against expected schema."""
