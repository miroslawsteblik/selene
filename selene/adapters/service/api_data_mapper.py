from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, List, Optional

from selene.domains.market_data.entities.market_data import DataSource, MarketData
from selene.ports.market_data.service.api_data_mapper import DataMapperPort


class SafeDataMapper(DataMapperPort):
    """Safe implementation of DataMapperPort with error handling."""

    def __init__(self, schema_config: Optional[Dict[str, Any]] = None) -> None:
        # Define expected schema mappings with fallbacks
        if schema_config:
            self.schema_mappings = {"api": schema_config}
        else:
            # Default to alpha_vantage global_quote schema
            self.schema_mappings = {
                "api": {
                    "price_path": ["Global Quote", "05. price"],
                    "volume_path": ["Global Quote", "06. volume"],
                    "market_cap_path": None,
                    "pe_ratio_path": None,
                    "timestamp_path": ["Global Quote", "07. latest trading day"],
                    "validation_keys": ["Global Quote"],
                }
            }

    def map_to_market_data(self, api_data: Dict[str, Any], symbol: str) -> MarketData:
        """Safely map API data to MarketData entity"""

        # Validate basic structure
        validation_errors = self.validate_api_schema(api_data)
        if validation_errors:
            raise ValueError(f"API schema validation failed: {validation_errors}")

        try:
            # Extract data with safe navigation
            schema = self.schema_mappings["api"]
            price = self._safe_extract_decimal(api_data, schema["price_path"])
            volume = self._safe_extract_int(api_data, schema["volume_path"])
            timestamp = self._safe_extract_datetime(api_data, schema["timestamp_path"])

            return MarketData(
                symbol=symbol.upper(),
                price=price or Decimal("0.00"),
                volume=volume or 0,
                market_cap=None,  # Not available in this API
                pe_ratio=None,  # Not available in this API
                data_timestamp=timestamp or datetime.now(),
                source=DataSource.API,
                raw_data=api_data,  # Store original for debugging
            )

        except Exception as e:
            raise ValueError(
                f"Failed to map API data for symbol {symbol}: {str(e)}"
            ) from e

    def validate_api_schema(self, api_data: Dict[str, Any]) -> List[str]:
        """Validate API response has expected structure"""
        errors = []

        # Validate required keys based on schema configuration
        schema = self.schema_mappings["api"]
        validation_keys = schema.get("validation_keys", [])

        for key in validation_keys:
            if key not in api_data:
                errors.append(f"Missing '{key}' in API response")

        # Check for error messages in API response
        if "Error Message" in api_data:
            errors.append(f"API Error: {api_data['Error Message']}")

        if "Note" in api_data:
            errors.append(f"API Limit: {api_data['Note']}")

        return errors

    def _safe_extract_decimal(
        self, data: Dict[str, Any], path: Optional[List[str]]
    ) -> Optional[Decimal]:
        """Safely extract decimal value from nested dictionary"""
        if not path:
            return None

        try:
            # Use the navigation helper for consistency
            value = self._navigate_path(data, path)
            if value is None:
                return None

            # Handle specific types
            if isinstance(value, Decimal):
                return value
            elif isinstance(value, (int, float)):
                return Decimal(str(value))
            elif isinstance(value, str):
                # Handle string representations
                value = value.strip()
                if not value:  # Handle empty strings
                    return None
                return Decimal(value)
            else:
                # Last resort
                return Decimal(str(value))
        except (InvalidOperation, ValueError, TypeError):
            return None

    def _safe_extract_int(
        self, data: Dict[str, Any], path: Optional[List[str]]
    ) -> Optional[int]:
        """Safely extract integer value from nested dictionary"""
        if not path:
            return None

        try:
            # Navigate to the nested value
            value = self._navigate_path(data, path)
            if value is None:
                return None

            # Convert the value to int based on its type
            if isinstance(value, int):
                return value
            elif isinstance(value, float):
                return int(value)
            elif isinstance(value, str):
                # Convert string to float first to handle "123.45" strings
                return int(float(value))
            else:
                # Last resort - try string conversion
                return int(float(str(value)))
        except (ValueError, TypeError):
            return None

    def _navigate_path(self, data: Dict[str, Any], path: List[str]) -> Any:
        """Navigate a nested dictionary using a path list."""
        value = data
        for key in path:
            if not isinstance(value, dict) or key not in value:
                return None
            value = value[key]
            # if value is None:
            #     return None
        return value

    def _safe_extract_datetime(
        self, data: Dict[str, Any], path: Optional[List[str]]
    ) -> Optional[datetime]:
        """Safely extract datetime value from nested dictionary"""
        if not path:
            return None

        try:
            value = self._navigate_path(data, path)
            if not value:
                return None

            # Try more datetime formats and handle more cases
            if isinstance(value, datetime):
                return value

            if isinstance(value, str):
                for fmt in [
                    "%Y-%m-%d",
                    "%Y-%m-%d %H:%M:%S",
                    "%Y-%m-%dT%H:%M:%S",
                    "%Y-%m-%dT%H:%M:%S.%f",
                    "%Y/%m/%d",
                    "%d/%m/%Y",
                ]:
                    try:
                        return datetime.strptime(value, fmt)
                    except ValueError:
                        continue

            # Consider adding timestamp conversion if value is numeric
            if isinstance(value, (int, float)):
                try:
                    return datetime.fromtimestamp(value)
                except (ValueError, OverflowError):
                    pass

            # If we reach here, we couldn't parse the datetime
            return None
        except (ValueError, TypeError):
            return None
