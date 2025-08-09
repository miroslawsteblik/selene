from typing import Any, Dict, List

from selene.domains.market_data.service.market_data_service import MarketDataService


class FetchMarketDataUseCase:
    """Use case for fetching market data from API"""

    def __init__(self, market_data_service: MarketDataService):
        self.market_data_service = market_data_service

    def execute(self, symbols: List[str]) -> Dict[str, Any]:
        """Execute market data fetching"""
        try:
            # Fetch and store market data
            results = self.market_data_service.fetch_and_store_market_data(symbols)

            # Add summary
            results["summary"] = {
                "total_requested": len(symbols),
                "successful_count": len(results["successful"]),
                "failed_count": len(results["failed"]),
                "validation_error_count": len(results["validation_errors"]),
                "success_rate": (
                    len(results["successful"]) / len(symbols) if symbols else 0
                ),
            }

            return results

        except (KeyError, ValueError) as e:
            return {
                "error": str(e),
                "successful": [],
                "failed": [],
                "validation_errors": [],
                "summary": {"total_requested": len(symbols), "success_rate": 0},
            }
