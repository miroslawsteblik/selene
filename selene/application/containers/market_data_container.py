from typing import Optional

from selene.adapters.repository.postgres.api_log_repository import (
    PostgresAPILogRepository,
)
from selene.adapters.repository.postgres.market_data_repository import (
    PostgresMarketDataRepository,
)
from selene.adapters.service.alpha_vantage_api import AlphaVantageAPI
from selene.adapters.service.api_data_mapper import SafeDataMapper
from selene.domains.market_data.service.market_data_service import MarketDataService
from selene.infrastructure.database.connection_factory import PostgresConnectionFactory
from selene.infrastructure.database.db_config import DatabaseConnectionConfig
from selene.infrastructure.logging.logger_factory import AppLoggerFactory

from ...application.use_cases.fetch_market_data_use_case import FetchMarketDataUseCase
from ...infrastructure.configuration.config_loader import (
    ConfigurationError,
    ConfigurationLoader,
)
from ...infrastructure.configuration.market_data_config import MarketDataConfig


class MarketDataContainer:

    def __init__(self, config_path: str):
        self._config: Optional[MarketDataConfig] = None
        self._config_loader = ConfigurationLoader(config_path)
        self._logger = AppLoggerFactory.create_logger(__name__)

    @property
    def config(self) -> MarketDataConfig:
        """Get configuration (lazy-loaded with caching)"""
        if self._config is None:
            try:
                self._logger.debug("Loading configuration...")
                self._config = self._config_loader.load_config()
                self._logger.info("Configuration loaded successfully")
            except ConfigurationError as e:
                self._logger.error(f"Configuration loading failed: {e}")
                raise
            except Exception as e:
                self._logger.error(f"Unexpected error loading configuration: {e}")
                raise ConfigurationError(f"Failed to load configuration: {e}")

        return self._config

    def _create_db_config(self) -> DatabaseConnectionConfig:
        """Get database config object for connection factory"""
        config = self.config
        # Configuration now directly provides DatabaseConnectionConfig
        return config.database

    def create_use_case(self) -> FetchMarketDataUseCase:
        """Create use case for fetching market data with all dependencies."""
        config = self.config

        # Convert config format and create connection factory
        db_config = self._create_db_config()
        self._connection_factory = PostgresConnectionFactory(db_config, self._logger)
        self._connection_factory.initialize()

        # Create adapters
        api_adapter = AlphaVantageAPI(config.api.api_key, config.api.base_url)
        data_mapper = SafeDataMapper()
        market_data_repo = PostgresMarketDataRepository(self._connection_factory)
        api_log_repo = PostgresAPILogRepository(self._connection_factory)

        # Authenticate API
        if not api_adapter.authenticate():
            raise ValueError("Failed to authenticate with API")

        # Create domain service
        market_data_service = MarketDataService(
            api_port=api_adapter,
            data_mapper=data_mapper,
            market_data_repository=market_data_repo,
            api_log_repository=api_log_repo,
        )

        # Create use case
        return FetchMarketDataUseCase(market_data_service)

    def cleanup(self) -> None:
        """Clean up resources held by the container"""
        if (
            hasattr(self, "_connection_factory")
            and self._connection_factory is not None
        ):
            self._logger.info("Closing database connections")
            self._connection_factory.close()
            # Mark as None, type ignored as it's cleared on exit
            self._connection_factory = None  # type: ignore
