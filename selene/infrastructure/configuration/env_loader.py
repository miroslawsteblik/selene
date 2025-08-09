import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


class EnvironmentLoader:
    """Handles loading environment variables from .env files"""

    def __init__(self, env_file: Optional[str] = None):
        self.env_file = env_file
        self._load_environment()

    def _load_environment(self) -> None:
        """Load environment variables with precedence"""
        # 1. Load from specific file if provided
        if self.env_file and Path(self.env_file).exists():
            load_dotenv(self.env_file, override=False)
            return

        # 2. Load environment-specific file
        environment = os.getenv("ENVIRONMENT", "development")
        env_file = f".env.{environment}"

        if Path(env_file).exists():
            load_dotenv(env_file, override=False)

        # 3. Load default .env file (fallback)
        if Path(".env").exists():
            load_dotenv(".env", override=False)

    def get_secret(
        self, key: str, required: bool = True, default: Optional[str] = None
    ) -> str:
        """Get secret from environment with validation"""
        value = os.getenv(key, default)

        if required and value is None:
            raise EnvironmentError(f"Required environment variable '{key}' not found")

        if value is None:
            return default if default is not None else ""

        # Basic validation for common secrets
        if "KEY" in key and len(value.strip()) < 8:
            raise ValueError(
                f"Environment variable '{key}' appears to be too short for a valid key"
            )

        return value.strip()

    def get_int(
        self, key: str, required: bool = True, default: Optional[int] = None
    ) -> Optional[int]:
        """Get integer from environment"""
        value = self.get_secret(
            key, required, str(default) if default is not None else None
        )

        try:
            return int(value)
        except ValueError as exc:
            raise ValueError(
                f"Environment variable '{key}' must be an integer, got: {value}"
            ) from exc

    def get_bool(
        self, key: str, required: bool = True, default: Optional[bool] = None
    ) -> Optional[bool]:
        """Get boolean from environment"""
        value = self.get_secret(
            key, required, str(default).lower() if default is not None else None
        )

        return value.lower() in ("true", "1", "yes", "on")

    def get_list(
        self,
        key: str,
        delimiter: str = ",",
        required: bool = True,
        default: Optional[list] = None,
    ) -> Optional[list]:
        """Get list from environment (comma-separated by default)"""
        value = self.get_secret(
            key, required, delimiter.join(default) if default else None
        )

        return [item.strip() for item in value.split(delimiter) if item.strip()]
