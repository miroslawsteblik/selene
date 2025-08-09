from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict


@dataclass(frozen=True)
class APIResponse:
    """Value object for API response data"""

    status_code: int
    data: Dict[str, Any]
    headers: Dict[str, str]
    execution_time_ms: int
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def is_successful(self) -> bool:
        return 200 <= self.status_code < 300

    @property
    def has_data(self) -> bool:
        return bool(self.data)
