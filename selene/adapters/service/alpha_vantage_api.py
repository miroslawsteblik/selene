import time
from typing import List

import requests

from selene.domains.market_data.value_objects.api_response import APIResponse
from selene.ports.market_data.service.market_data_api import MarketDataAPIPort


class AlphaVantageAPI(MarketDataAPIPort):
    """Implementation of MarketDataAPIPort for Alpha Vantage API."""

    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update(
            {"User-Agent": "selene/1.0", "Accept": "application/json"}
        )
        self.authenticated = False

    def authenticate(self) -> bool:
        """Authenticate with the Alpha Vantage API."""
        try:
            # start_time = time.time()
            response = self.session.get(
                self.base_url,
                params={
                    "function": "TIME_SERIES_DAILY",
                    "symbol": "AAPL",
                    "interval": "1min",
                    "apikey": self.api_key,
                    "outputsize": "compact",
                },
                timeout=30,
            )
            # execution_time_ms = int((time.time() - start_time) * 1000)

            if response.status_code == 200:
                data = response.json()
                if "Error Message" not in data:
                    self.authenticated = True
                    return True
            self.authenticated = False
            return False
        except requests.RequestException as e:
            raise ConnectionError(
                f"Failed to authenticate with Alpha Vantage API: {e}"
            ) from e
        except Exception as e:
            raise RuntimeError(
                f"An unexpected error occurred during authentication: {e}"
            ) from e

    def get_market_data(self, symbol: str) -> APIResponse:
        """Fetch market data for a given symbol."""
        if not self.authenticated:
            raise PermissionError("API not authenticated")
        start_time = time.time()

        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": self.api_key,
        }
        try:
            response = self.session.get(
                self.base_url,
                params=params,
                timeout=30,
            )
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

    def is_authenticated(self) -> bool:
        """Check if the API is authenticated."""
        return self.authenticated
        return self.authenticated
        return self.authenticated
