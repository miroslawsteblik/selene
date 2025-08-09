from abc import ABC, abstractmethod
from typing import List

from selene.domains.market_data.entities.api_log import APILog


class APILogRepositoryPort(ABC):
    """Repository interface for API logs"""

    @abstractmethod
    def save(self, log_entry: APILog) -> APILog:
        """Save API log entry"""

    @abstractmethod
    def find_recent_errors(self, hours: int = 24) -> List[APILog]:
        """Find recent API errors"""
