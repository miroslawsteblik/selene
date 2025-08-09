from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional


class DataSource(Enum):
    API = "API"
    CSV = "CSV"
    MANUAL = "MANUAL"


class DataStatus(Enum):
    PENDING = "PENDING"
    VALIDATED = "VALIDATED"
    FAILED = "FAILED"
    SAVED = "SAVED"


@dataclass
class MarketData:
    """Domain Entity for API market data"""

    id: Optional[int] = None
    symbol: str = ""
    price: Decimal = Decimal("0.00")
    volume: int = 0
    market_cap: Optional[Decimal] = None
    pe_ratio: Optional[Decimal] = None
    data_timestamp: Optional[datetime] = None
    source: DataSource = DataSource.API
    status: DataStatus = DataStatus.PENDING
    raw_data: Dict[str, Any] = field(
        default_factory=dict
    )  # Store original API response
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self) -> None:
        if self.created_at is None:
            self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def validate(self) -> List[str]:
        """Business validation rules"""
        errors = []

        if not self.symbol.strip():
            errors.append("Symbol is required")

        if self.price <= 0:
            errors.append("Price must be positive")

        if self.volume < 0:
            errors.append("Volume cannot be negative")

        if self.market_cap is not None and self.market_cap <= 0:
            errors.append("Market cap must be positive if provided")

        if self.pe_ratio is not None and self.pe_ratio <= 0:
            errors.append("PE ratio must be positive if provided")

        if self.data_timestamp is None:
            errors.append("Data timestamp is required")

        return errors

    def is_valid(self) -> bool:
        return len(self.validate()) == 0

    def mark_as_validated(self) -> None:
        """Business behavior"""
        if self.is_valid():
            self.status = DataStatus.VALIDATED
            self.updated_at = datetime.now()
        else:
            raise ValueError(f"Cannot validate: {self.validate()}")

    def mark_as_saved(self) -> None:
        """Business behavior"""
        if self.status == DataStatus.VALIDATED:
            self.status = DataStatus.SAVED
            self.updated_at = datetime.now()
        else:
            raise ValueError("Only validated data can be marked as saved")
