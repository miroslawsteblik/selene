import logging
import threading
from contextlib import contextmanager
from tracemalloc import Traceback
from typing import Any, Dict, Generator, Optional

import psycopg2
import psycopg2.pool
from selene.infrastructure.database.db_config import DatabaseConnectionConfig
from selene.infrastructure.logging.logger_factory import AppLoggerFactory


class PostgresConnectionFactory:
    """Factory for creating and managing database connections."""

    def __init__(
        self, config: DatabaseConnectionConfig, logger: Optional[logging.Logger] = None
    ):
        self.config = config
        self.logger = AppLoggerFactory.create_logger(__name__)
        self._pool: Optional[psycopg2.pool.SimpleConnectionPool] = None
        self._lock = threading.Lock()

    def initialize(self) -> None:
        """Initialize the connection pool"""
        try:
            with self._lock:
                if self._pool is not None:
                    self.logger.warning("Connection pool already initialized")
                    return

                self.logger.info(
                    "Initializing PostgreSQL connection pool: %d-%d connections",
                    self.config.min_connections,
                    self.config.max_connections,
                )

                self._pool = psycopg2.pool.SimpleConnectionPool(
                    minconn=self.config.min_connections,
                    maxconn=self.config.max_connections,
                    **self.config.to_dict(),
                )

                # Test the connection
                self._test_connection()
                self.logger.info("PostgreSQL connection pool initialized successfully")

        except Exception as e:
            self.logger.error("Failed to initialize connection pool: %s", e)
            raise

    def _test_connection(self) -> None:
        """Test database connectivity"""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT version();")
                version = cursor.fetchone()
                if version:
                    version = version[0]
                else:
                    version = "Unknown"
                self.logger.info("Connected to PostgreSQL: %s", version)

    @contextmanager
    def get_connection(self) -> Generator[psycopg2.extensions.connection, None, None]:
        """
        Get a connection from the pool using context manager

        Usage:
            with factory.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT * FROM users")
                    results = cursor.fetchall()
        """
        if self._pool is None:
            raise RuntimeError(
                "Connection pool not initialized. Call initialize() first."
            )

        connection = None
        try:
            connection = self._pool.getconn()
            if connection is None:
                raise RuntimeError("Failed to get connection from pool")

            # Reset connection state
            connection.autocommit = False

            self.logger.debug("Connection acquired from pool")
            yield connection

        except Exception as e:
            self.logger.error("Error getting connection: %s", e)
            if connection:
                connection.rollback()
            raise
        finally:
            if connection:
                try:
                    # Ensure transaction is committed or rolled back
                    if connection.status == psycopg2.extensions.STATUS_IN_TRANSACTION:
                        connection.rollback()

                    self._pool.putconn(connection)
                    self.logger.debug("Connection returned to pool")
                except (psycopg2.DatabaseError, psycopg2.InterfaceError) as e:
                    self.logger.error("Error returning connection to pool: %s", e)

    @contextmanager
    def get_cursor(self) -> Generator[psycopg2.extensions.cursor, None, None]:
        """
        Get a cursor with automatic connection management

        Usage:
            with factory.get_cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
                result = cursor.fetchone()
        """
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                try:
                    yield cursor
                    conn.commit()
                except Exception:
                    conn.rollback()
                    raise

    def execute_query(self, query: str, params: tuple) -> Any:
        """
        Execute a SELECT query and return results

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            List of query results
        """
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()

    def execute_update(self, query: str, params: tuple) -> Any:
        """
        Execute INSERT/UPDATE/DELETE query

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            Number of affected rows
        """
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.rowcount

    def execute_many(self, query: str, params_list: list) -> Any:
        """
        Execute query with multiple parameter sets

        Args:
            query: SQL query string
            params_list: List of parameter tuples

        Returns:
            Number of affected rows
        """
        with self.get_cursor() as cursor:
            cursor.executemany(query, params_list)
            return cursor.rowcount

    def get_pool_status(self) -> Dict[str, Any]:
        """Get current pool status"""
        if not self._pool:
            return {"status": "not_initialized"}

        return {
            "status": "active",
            "min_connections": self.config.min_connections,
            "max_connections": self.config.max_connections,
            "closed": self._pool.closed,
        }

    def close(self) -> None:
        """Close all connections in the pool"""
        if self._pool:
            with self._lock:
                try:
                    self._pool.closeall()
                    self.logger.info("All database connections closed")
                except (psycopg2.DatabaseError, psycopg2.InterfaceError) as e:
                    self.logger.error("Error closing connection pool: %s", e)
                finally:
                    self._pool = None

    def __enter__(self) -> "PostgresConnectionFactory":
        """Context manager entry"""
        self.initialize()
        return self

    def __exit__(self, exc_type: type, exc_val: Exception, exc_tb: Traceback) -> None:
        """Context manager exit"""
        self.close()
