import json
from datetime import datetime, timedelta
from typing import List

from selene.domains.market_data.entities.api_log import APILog
from selene.infrastructure.database.connection_factory import PostgresConnectionFactory
from selene.ports.outbound.api_log_repository_port import APILogRepositoryPort


class PostgresAPILogRepository(APILogRepositoryPort):
    """PostgreSQL implementation for API logs"""

    def __init__(self, connection_factory: PostgresConnectionFactory) -> None:
        self.db = connection_factory
        self._ensure_tables()

    def _ensure_tables(self) -> None:
        """Create API log tables"""
        with self.db.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS api_logs (
                        id SERIAL PRIMARY KEY,
                        operation VARCHAR(100) NOT NULL,
                        endpoint VARCHAR(255) NOT NULL,
                        status_code INTEGER,
                        success BOOLEAN NOT NULL DEFAULT FALSE,
                        error_message TEXT,
                        request_data JSONB,
                        response_data JSONB,
                        execution_time_ms INTEGER,
                        timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                    );

                    CREATE INDEX IF NOT EXISTS idx_api_logs_timestamp
                    ON api_logs(timestamp);
                    CREATE INDEX IF NOT EXISTS idx_api_logs_success
                    ON api_logs(success);
                    CREATE INDEX IF NOT EXISTS idx_api_logs_operation
                    ON api_logs(operation);
                """
                )
                conn.commit()

    def save(self, log_entry: APILog) -> APILog:
        """Save API log entry"""
        with self.db.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO api_logs
                    (operation, endpoint, status_code, success, error_message,
                     request_data, response_data, execution_time_ms, timestamp)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """,
                    (
                        log_entry.operation,
                        log_entry.endpoint,
                        log_entry.status_code,
                        log_entry.success,
                        log_entry.error_message,
                        json.dumps(log_entry.request_data),
                        json.dumps(log_entry.response_data),
                        log_entry.execution_time_ms,
                        log_entry.timestamp,
                    ),
                )

                result = cursor.fetchone()
                if result is not None:
                    log_entry.id = result[0]
                else:
                    log_entry.id = None
                conn.commit()
                return log_entry

    def find_recent_errors(self, hours: int = 24) -> List[APILog]:
        """Find recent API errors"""
        cutoff_time = datetime.now() - timedelta(hours=hours)

        with self.db.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT * FROM api_logs
                    WHERE success = FALSE AND timestamp >= %s
                    ORDER BY timestamp DESC
                """,
                    (cutoff_time,),
                )

                return [self._row_to_api_log(row) for row in cursor.fetchall()]

    def _row_to_api_log(self, row: tuple) -> APILog:
        """Convert database row to APILog entity"""
        return APILog(
            id=row[0],
            operation=row[1],
            endpoint=row[2],
            status_code=row[3],
            success=row[4],
            error_message=row[5],
            request_data=row[6] or {},
            response_data=row[7] or {},
            execution_time_ms=row[8],
            timestamp=row[9],
        )
