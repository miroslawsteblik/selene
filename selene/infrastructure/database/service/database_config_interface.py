from abc import ABC, abstractmethod
from typing import Any, Dict


class DatabaseConfigInterface(ABC):
    """
    Interface for database configuration objects.

    This interface defines the common contract that all database configuration
    classes must implement, regardless of their source or usage.
    """

    @property
    @abstractmethod
    def host(self) -> str:
        """Get database host."""

    @property
    @abstractmethod
    def port(self) -> int:
        """Get database port."""

    @property
    @abstractmethod
    def database(self) -> str:
        """Get database name."""

    @property
    @abstractmethod
    def user(self) -> str:
        """Get database user."""

    @property
    @abstractmethod
    def password(self) -> str:
        """Get database password."""

    @property
    @abstractmethod
    def min_connections(self) -> int:
        """Get minimum connections for pool."""

    @property
    @abstractmethod
    def max_connections(self) -> int:
        """Get maximum connections for pool."""

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""

    @property
    @abstractmethod
    def connection_string(self) -> str:
        """Generate connection string."""
