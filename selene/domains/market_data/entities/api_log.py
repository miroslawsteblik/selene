from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class APILog:
    """Domain Entity for API operation logging"""

    id: Optional[int] = None
    operation: str = ""
    endpoint: str = ""
    status_code: Optional[int] = None
    success: bool = False
    error_message: Optional[str] = None
    request_data: Dict[str, Any] = field(default_factory=dict)
    response_data: Dict[str, Any] = field(default_factory=dict)
    execution_time_ms: Optional[int] = None
    timestamp: Optional[datetime] = None

    def __post_init__(self) -> None:
        if self.timestamp is None:
            self.timestamp = datetime.now()
