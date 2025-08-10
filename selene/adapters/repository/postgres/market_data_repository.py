import json
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Optional

from selene.domains.market_data.entities.market_data import (
    DataSource,
    DataStatus,
    MarketData,
)
from selene.infrastructure.database.connection_factory import PostgresConnectionFactory
from selene.ports.market_data.repository.market_data_ports import (
    MarketDataRepositoryPort,
)


class PostgresMarketDataRepository(MarketDataRepositoryPort):
    """PostgreSQL implementation for MarketData repository"""

    def __init__(self, connection_factory: PostgresConnectionFactory) -> None:
        self.db = connection_factory
        self._ensure_tables()

    def _ensure_tables(self) -> None:
        """Create tables if they don't exist"""
        with self.db.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS market_data (
                        id SERIAL PRIMARY KEY,
                        symbol VARCHAR(20) NOT NULL,
                        price DECIMAL(15,4) NOT NULL,
                        volume BIGINT NOT NULL DEFAULT 0,
                        market_cap DECIMAL(20,2),
                        pe_ratio DECIMAL(10,2),
                        data_timestamp TIMESTAMP NOT NULL,
                        source VARCHAR(20) NOT NULL DEFAULT 'API',
                        status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
                        raw_data JSONB,
                        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                    );

                    CREATE INDEX IF NOT EXISTS idx_market_data_symbol
                    ON market_data(symbol);
                    CREATE INDEX IF NOT EXISTS idx_market_data_timestamp
                    ON market_data(data_timestamp);
                    CREATE INDEX IF NOT EXISTS idx_market_data_status
                    ON market_data(status);
                """
                )
                conn.commit()

    def save(self, market_data: MarketData) -> MarketData:
        """Save market data to PostgreSQL"""
        with self.db.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO market_data
                    (symbol, price, volume, market_cap, pe_ratio, data_timestamp,
                     source, status, raw_data, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """,
                    (
                        market_data.symbol,
                        float(market_data.price),
                        market_data.volume,
                        (
                            float(market_data.market_cap)
                            if market_data.market_cap
                            else None
                        ),
                        float(market_data.pe_ratio) if market_data.pe_ratio else None,
                        market_data.data_timestamp,
                        market_data.source.value,
                        market_data.status.value,
                        json.dumps(market_data.raw_data),
                        market_data.created_at,
                        market_data.updated_at,
                    ),
                )

                result = cursor.fetchone()
                if result is not None:
                    market_data.id = result[0]
                else:
                    market_data.id = None
                conn.commit()
                return market_data

    def update(self, market_data: MarketData) -> MarketData:
        """Update existing market data"""
        if not market_data.id:
            raise ValueError("Cannot update MarketData without ID")

        market_data.updated_at = datetime.now()

        with self.db.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE market_data
                    SET price = %s, volume = %s, market_cap = %s, pe_ratio = %s,
                        data_timestamp = %s, source = %s, status = %s,
                        raw_data = %s, updated_at = %s
                    WHERE id = %s
                """,
                    (
                        float(market_data.price),
                        market_data.volume,
                        (
                            float(market_data.market_cap)
                            if market_data.market_cap
                            else None
                        ),
                        float(market_data.pe_ratio) if market_data.pe_ratio else None,
                        market_data.data_timestamp,
                        market_data.source.value,
                        market_data.status.value,
                        json.dumps(market_data.raw_data),
                        market_data.updated_at,
                        market_data.id,
                    ),
                )
                conn.commit()
                return market_data

    def find_by_symbol(self, symbol: str) -> Optional[MarketData]:
        """Find latest market data by symbol"""
        with self.db.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT * FROM market_data
                    WHERE symbol = %s
                    ORDER BY data_timestamp DESC
                    LIMIT 1
                """,
                    (symbol,),
                )

                row = cursor.fetchone()
                if row:
                    return self._row_to_market_data(row)
                return None

    def find_all_recent(self, hours: int = 24) -> List[MarketData]:
        """Find all recent market data"""
        cutoff_time = datetime.now() - timedelta(hours=hours)

        with self.db.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT * FROM market_data
                    WHERE data_timestamp >= %s
                    ORDER BY data_timestamp DESC
                """,
                    (cutoff_time,),
                )

                return [self._row_to_market_data(row) for row in cursor.fetchall()]

    def _row_to_market_data(self, row: tuple) -> MarketData:
        """Convert database row to MarketData entity"""
        return MarketData(
            id=row[0],
            symbol=row[1],
            price=Decimal(str(row[2])),
            volume=row[3],
            market_cap=Decimal(str(row[4])) if row[4] else None,
            pe_ratio=Decimal(str(row[5])) if row[5] else None,
            data_timestamp=row[6],
            source=DataSource(row[7]),
            status=DataStatus(row[8]),
            raw_data=row[9] or {},
            created_at=row[10],
            updated_at=row[11],
        )
