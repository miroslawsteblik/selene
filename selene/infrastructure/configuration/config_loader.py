from pathlib import Path
from typing import Any, Dict

import yaml

from selene.infrastructure.configuration.env_loader import EnvironmentLoader
from selene.infrastructure.configuration.market_data_config import (
    APIConfig,
    MarketDataConfig,
)
from selene.infrastructure.database.db_config import DatabaseConnectionConfig


class ConfigurationLoader:
    """Loads and validates configuration from YAML files and environment variables"""

    def __init__(self, config_path: str = "config"):
        self.config_path = Path(config_path)
        self.env_loader = EnvironmentLoader()

    def load_config(self) -> MarketDataConfig:
        """Load configuration with environment variable substitution"""
        try:
            # Load base configuration from YAML
            config_file = self.config_path

            if not config_file.exists():
                raise FileNotFoundError(f"Configuration file not found: {config_file}")

            with open(config_file, "r", encoding="utf-8") as file:
                yaml_config = yaml.safe_load(file)

            # Build typed configuration objects
            config = self._build_config_with_env(yaml_config)

            # Validate configuration
            # config.validate()

            return config

        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration: {str(e)}") from e

    def _build_config_with_env(self, yaml_config: Dict[str, Any]) -> MarketDataConfig:
        """Build configuration using environment variables for secrets"""

        # Build API config
        api_data = yaml_config.get("api", {})
        api_config = APIConfig(
            base_url=api_data.get("base_url", ""),
            api_key=self.env_loader.get_secret("ALPHA_VANTAGE_API_KEY"),  # From .env
            timeout_seconds=api_data.get("timeout_seconds", 30),
            retry_attempts=api_data.get("retry_attempts", 3),
            rate_limit_per_minute=api_data.get("rate_limit_per_minute", 60),
        )

        # Database Configuration - Create DatabaseConnectionConfig directly
        db_data = yaml_config.get("database", {})

        database_config = DatabaseConnectionConfig(
            host=self.env_loader.get_secret(
                "DB_HOST", default=db_data.get("host", "localhost")
            ),
            port=self.env_loader.get_int("DB_PORT", default=db_data.get("port", 5432))
            or 5432,
            database=self.env_loader.get_secret(
                "DB_NAME", default=db_data.get("database", "")
            ),
            user=self.env_loader.get_secret("DB_USER", default=db_data.get("user", "")),
            password=self.env_loader.get_secret("DB_PASSWORD", default=""),
            min_connections=self.env_loader.get_int(
                "DB_MIN_CONNECTIONS", default=db_data.get("min_connection", 5)
            )
            or 5,
            max_connections=self.env_loader.get_int(
                "DB_MAX_CONNECTIONS", default=db_data.get("max_connection", 10)
            )
            or 10,
            connect_timeout=30,
            app_name="selene",
        )

        return MarketDataConfig(
            api=api_config,
            database=database_config,
        )


class ConfigurationError(Exception):
    """Custom exception for configuration-related errors"""

    """Custom exception for configuration-related errors"""
    """Custom exception for configuration-related errors"""
