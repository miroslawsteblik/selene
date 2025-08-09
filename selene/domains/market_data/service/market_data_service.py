from typing import Any, Dict, List

from selene.domains.market_data.entities.api_log import APILog
from selene.infrastructure.logging.logger_factory import AppLoggerFactory
from selene.ports.market_data.repository.api_log_ports import APILogRepositoryPort
from selene.ports.market_data.repository.market_data_ports import (
    MarketDataRepositoryPort,
)
from selene.ports.market_data.service.api_data_mapper import DataMapperPort
from selene.ports.market_data.service.market_data_api import MarketDataAPIPort


class MarketDataService:

    def __init__(
        self,
        api_port: MarketDataAPIPort,
        data_mapper: DataMapperPort,
        market_data_repository: MarketDataRepositoryPort,
        api_log_repository: APILogRepositoryPort,
    ):
        self.api_port = api_port
        self.data_mapper = data_mapper
        self.market_data_repository = market_data_repository
        self.api_log_repository = api_log_repository
        self.logger = AppLoggerFactory.create_logger(__name__)

    def fetch_and_store_market_data(self, symbols: List[str]) -> Dict[str, Any]:
        """Fetch market data for multiple symbols and store in database."""
        self.logger.info(
            "Starting market data fetch for %d symbols: %s", len(symbols), symbols
        )

        results: Dict[str, Any] = {
            "successful": [],
            "failed": [],
            "validation_errors": [],
        }

        for symbol in symbols:
            try:
                self.logger.debug("Processing symbol: %s", symbol)
                self._process_symbol(symbol, results)
            except (ValueError, KeyError) as e:
                self.logger.error("Known error processing symbol %s: %s", symbol, e)
                self._handle_unexpected_error(symbol, e, results)
            except RuntimeError as e:
                self.logger.error("Runtime error processing symbol %s: %s", symbol, e)
                self._handle_unexpected_error(symbol, e, results)
            except IOError as e:
                self.logger.error("IO error processing symbol %s: %s", symbol, e)
                self._handle_unexpected_error(symbol, e, results)

        self.logger.info(
            "Fetch completed. Success: %d, Failed: %d, Validation errors: %d",
            len(results["successful"]),
            len(results["failed"]),
            len(results["validation_errors"]),
        )
        return results

    def _process_symbol(self, symbol: str, results: Dict[str, Any]) -> None:
        """Process a single symbol through the complete pipeline."""
        # Fetch data from API
        api_response = self._fetch_api_data(symbol)
        if not api_response:
            results["failed"].append(symbol)
            return

        # Log API call
        self._log_api_call(symbol, api_response)

        if not api_response.is_successful:
            self._handle_api_error(symbol, api_response, results)
            return

        # Map and validate data
        try:
            market_data = self._map_and_validate_data(symbol, api_response, results)
            if not market_data:
                return
        except ValueError as e:
            self._handle_mapping_error(symbol, e, api_response, results)
            return

        # Save to database
        self._save_market_data(symbol, market_data, results)

    def _fetch_api_data(self, symbol: str):
        """Fetch data from API for a symbol."""
        self.logger.debug("Fetching API data for %s", symbol)
        return self.api_port.get_market_data(symbol)

    def _log_api_call(self, symbol: str, api_response) -> None:
        """Log the API call details."""
        log_entry = APILog(
            operation="fetch_market_data",
            endpoint=f"/market/{symbol}",
            status_code=api_response.status_code,
            success=api_response.is_successful,
            response_data=api_response.data,
            execution_time_ms=api_response.execution_time_ms,
        )
        self.api_log_repository.save(log_entry)

    def _handle_api_error(
        self, symbol: str, api_response, results: Dict[str, Any]
    ) -> None:
        """Handle API response errors."""
        error_msg = f"API returned {api_response.status_code}"
        self.logger.warning("API error for %s: %s", symbol, error_msg)
        results["failed"].append(
            {
                "symbol": symbol,
                "error": error_msg,
            }
        )

    def _map_and_validate_data(
        self, symbol: str, api_response, results: Dict[str, Any]
    ):
        """Map API response to domain entity and validate."""
        self.logger.debug("Mapping and validating data for %s", symbol)

        # Map API data to domain entity
        market_data = self.data_mapper.map_to_market_data(api_response.data, symbol)

        # Business validation
        if not market_data.is_valid():
            validation_errors = market_data.validate()
            self.logger.warning(
                "Validation failed for %s: %s", symbol, validation_errors
            )
            results["validation_errors"].append(
                {"symbol": symbol, "errors": validation_errors}
            )
            return None

        # Mark as validated
        market_data.mark_as_validated()
        self.logger.debug("Data validation successful for %s", symbol)
        return market_data

    def _handle_mapping_error(
        self, symbol: str, error: ValueError, api_response, results: Dict[str, Any]
    ) -> None:
        """Handle data mapping errors."""
        error_msg = f"Data mapping failed: {str(error)}"
        self.logger.error("Mapping error for %s: %s", symbol, error_msg)

        results["failed"].append(
            {
                "symbol": symbol,
                "error": error_msg,
            }
        )

        # Log mapping error
        error_log = APILog(
            operation="data_mapping",
            endpoint=f"/market/{symbol}",
            success=False,
            error_message=str(error),
            response_data=api_response.data,
        )
        self.api_log_repository.save(error_log)

    def _save_market_data(
        self, symbol: str, market_data, results: Dict[str, Any]
    ) -> None:
        """Save market data to database."""
        self.logger.debug("Saving market data for %s", symbol)

        # Save to database
        saved_data = self.market_data_repository.save(market_data)
        saved_data.mark_as_saved()
        self.market_data_repository.update(saved_data)

        results["successful"].append(saved_data)
        self.logger.debug("Successfully saved market data for %s", symbol)

    def _handle_unexpected_error(
        self, symbol: str, error: Exception, results: Dict[str, Any]
    ) -> None:
        """Handle unexpected errors during processing."""
        error_msg = str(error)
        self.logger.error("Unexpected error for %s: %s", symbol, error_msg)

        results["failed"].append({"symbol": symbol, "error": error_msg})

        # Log unexpected errors
        error_log = APILog(
            operation="fetch_and_store",
            endpoint=f"/market/{symbol}",
            success=False,
            error_message=error_msg,
        )
        self.api_log_repository.save(error_log)
