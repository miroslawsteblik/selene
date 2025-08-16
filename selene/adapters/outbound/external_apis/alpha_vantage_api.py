import time
from typing import List

import requests

from selene.domains.market_data.value_objects.api_response import APIResponse
from selene.infrastructure.logging.logger_factory import AppLoggerFactory
from selene.ports.outbound.market_data_api import MarketDataAPIPort


class AlphaVantageAPI(MarketDataAPIPort):
    """Implementation of MarketDataAPIPort for Alpha Vantage API."""

    def __init__(self, base_url: str, params: dict):
        self.base_url = base_url
        self.params = params
        self.session = requests.Session()
        self.session.headers.update(
            {"User-Agent": "selene/1.0", "Accept": "application/json"}
        )
        self.logger = AppLoggerFactory.create_logger(__name__)

    def get_market_data(self, symbol: str) -> APIResponse:
        """Fetch market data for a given symbol."""

        start_time = time.time()

        try:
            request_params = self.params.copy()
            request_params["symbol"] = symbol

            response = self.session.get(
                self.base_url,
                params=request_params,
                timeout=30,
            )
            self.logger.info("Response: %s %s", response.status_code, response.text)
            execution_time_ms = int((time.time() - start_time) * 1000)
            return APIResponse(
                status_code=response.status_code,
                data=response.json() if response.status_code == 200 else {},
                headers=dict(response.headers),
                execution_time_ms=execution_time_ms,
            )
        except requests.RequestException as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            return APIResponse(
                status_code=500,
                data={"error": str(e)},
                headers={},
                execution_time_ms=execution_time_ms,
            )

    def get_bulk_market_data(self, symbols: List[str]) -> APIResponse:
        """Fetch market data for multiple symbols"""
        # Alpha Vantage doesn't support bulk requests, so we'd need to call sequentially
        # This is just a placeholder - in practice, you'd implement rate limiting
        raise NotImplementedError("Bulk requests not supported by Alpha Vantage")
