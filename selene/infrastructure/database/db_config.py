from typing import Any, Dict

from selene.infrastructure.database.service.database_config_interface import (
    DatabaseConfigInterface,
)


class DatabaseConnectionConfig(DatabaseConfigInterface):
    """Database configuration with secure defaults and validation."""

    def __init__(
        self,
        host: str,
        port: int,
        user: str,
        password: str,
        database: str,
        min_connections: int = 1,
        max_connections: int = 10,
        connect_timeout: int = 30,
        app_name: str = "selene",
    ):
        self._host = host
        self._port = port
        self._user = user
        self._password = password
        self._database = database
        self._min_connections = min_connections
        self._max_connections = max_connections
        self.connect_timeout = connect_timeout
        self.app_name = app_name

    # Implementation of abstract properties from DatabaseConfigInterface
    @property
    def host(self) -> str:
        return self._host

    @property
    def port(self) -> int:
        return self._port

    @property
    def database(self) -> str:
        return self._database

    @property
    def user(self) -> str:
        return self._user

    @property
    def password(self) -> str:
        return self._password

    @property
    def min_connections(self) -> int:
        return self._min_connections

    @property
    def max_connections(self) -> int:
        return self._max_connections

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary for psycopg2"""
        return {
            "host": self.host,
            "port": self.port,
            "database": self.database,
            "user": self.user,
            "password": self.password,
            "connect_timeout": self.connect_timeout,
            "application_name": self.app_name,
        }

    @property
    def connection_string(self) -> str:
        """Generate connection string for database"""
        return (
            f"postgresql://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.database}"
        )
