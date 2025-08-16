# selene

A robust and scalable market data fetching and storage system built with clean architecture principles. selene connects to financial data APIs, validates and transforms the data, and stores it in a PostgreSQL database with comprehensive logging and error handling.

## 🎯 Project Overview

selene is designed to:

- Fetch real-time market data from financial APIs (currently Alpha Vantage)
- Transform and validate data using safe mapping techniques
- Store data in PostgreSQL with proper connection pooling
- Provide comprehensive logging and monitoring
- Handle errors gracefully with detailed reporting

## 🏗️ Architecture

### Clean Architecture Implementation

The project follows **Clean Architecture** and **Hexagonal Architecture** patterns.


### Core Components

#### 1. **Domain Layer** (`domains/market_data/`)

- **Entities**: Core business objects (`MarketData`, `APILog`)
- **Services**: Business logic (`MarketDataService`)
- **Value Objects**: Immutable data containers

#### 2. **Application Layer** (`application/`)

- **Use Cases**: Application-specific business rules (`FetchMarketDataUseCase`)
- **Containers**: Dependency injection and orchestration (`MarketDataContainer`)

#### 3. **Adapters Layer** (`adapters/`)

- **CLI**: Command-line interface handling
- **Persistence**: Database persistence implementations
- **External APIs**: External service integrations (`AlphaVantageAPI`)


#### 4. **Infrastructure Layer** (`infrastructure/`)

- **Database**: Connection management and pooling
- **Configuration**: Environment-aware config loading
- **Logging**: Comprehensive logging with emoji-safe formatting

#### 5. **Ports** (`ports/`)

- **Interfaces**: Abstract contracts between layers

## 🔧 Key Features

### Robust Database Management

- **Connection Pooling**: Thread-safe PostgreSQL connection pool (1-10 connections)
- **Transaction Management**: Automatic commit/rollback with proper cleanup
- **Health Monitoring**: Connection health checks and automatic recovery

### Advanced Logging System

- **Multi-level Logging**: Debug, info, warning, error levels
- **Emoji-safe Output**: Cross-platform console compatibility
- **Log Rotation**: Automatic log file rotation (50MB main, 10MB stats)
- **Structured Logging**: Consistent formatting across all components

### Configuration Management

- **Environment-aware**: YAML + environment variables
- **Type Safety**: Validated configuration objects with proper typing
- **Security**: Secrets loaded from environment variables only
- **Flexible**: Support for multiple environments (dev, staging, prod)

### Error Handling & Resilience

- **Graceful Degradation**: Continues processing other symbols on individual failures
- **Detailed Error Reporting**: Categorized errors with proper context
- **API Logging**: Complete audit trail of all API interactions
- **Validation**: Multi-layer validation (API response, business rules, data integrity)

### Data Processing Pipeline

- **Safe Data Mapping**: Schema-aware transformation with error handling
- **Business Validation**: Domain-specific validation rules
- **Batch Processing**: Efficient processing of multiple symbols
- **Status Tracking**: Complete lifecycle tracking from fetch to storage

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL 12+
- Alpha Vantage API key

### Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/miroslawsteblik/selene.git
   cd selene
   ```

2. **Install dependencies**:

   ```bash
   pip install -e ".[dev]"
   ```

3. **Set up environment variables**:

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Configure database**:

   ```yaml
   # resources/fetch_api.yaml
   database:
     host: localhost
     port: 5432
     database: selene
     user: postgres
   ```

5. **Set environment variables**:
   ```bash
   export DB_PASSWORD=your_postgres_password
   export ALPHA_VANTAGE_API_KEY=your_api_key
   ```

### Usage

#### Basic Commands

```bash
# Fetch market data
selene fetch --config resources/fetch_api.yaml

# Verbose logging
selene fetch --config resources/fetch_api.yaml --verbose

# Quiet mode
selene fetch --config resources/fetch_api.yaml --quiet
```

#### Configuration

The system uses a two-tier configuration approach:

1. **YAML Configuration** (`resources/fetch_api.yaml`):

   ```yaml
   api:
     base_url: 'https://www.alphavantage.co/query'
     timeout_seconds: 30
     retry_attempts: 3
     rate_limit_per_minute: 60

   database:
     host: localhost
     port: 5432
     database: selene
     user: postgres
     min_connection: 1
     max_connection: 10
   ```

2. **Environment Variables** (secrets):
   ```bash
   DB_PASSWORD=your_database_password
   ALPHA_VANTAGE_API_KEY=your_api_key
   DB_HOST=localhost  # optional override
   DB_PORT=5432       # optional override
   ```


## 📈 Monitoring & Observability

### Logging Levels

- **DEBUG**: Detailed tracing for development
- **INFO**: General operational information
- **WARNING**: Recoverable issues (API errors, validation failures)
- **ERROR**: Serious problems requiring attention

### Log Outputs

- **Console**: Real-time feedback with emoji-safe formatting
- **Main Log**: `logs/selene_YYYY-MM-DD.log` (rotated at 50MB)
- **Stats Log**: `logs/selene_stats_YYYY-MM-DD.log` (rotated at 10MB)

### Metrics Tracking

```python
# Automatic success rate calculation
{
    "successful": [saved_data_objects],
    "failed": [{"symbol": "AAPL", "error": "API error"}],
    "validation_errors": [{"symbol": "GOOGL", "errors": [...]}],
    "summary": {"success_rate": 0.75}
}
```

## 🔍 Example Output

```bash
$ selene fetch --config resources/fetch_api.yaml --verbose

2025-08-09 14:57:20,588 - selene.application.containers.market_data_container - INFO - Configuration loaded successfully
2025-08-09 14:57:20,588 - selene.infrastructure.database.connection_factory - INFO - Initializing PostgreSQL connection pool: 1-10 connections
2025-08-09 14:57:20,597 - selene.infrastructure.database.connection_factory - INFO - Connected to PostgreSQL: PostgreSQL 16.9 (Ubuntu 16.9-0ubuntu0.24.04.1)
2025-08-09 14:57:20,597 - selene.infrastructure.database.connection_factory - INFO - PostgreSQL connection pool initialized successfully
2025-08-09 14:57:21,848 - selene.adapters.cli.cli_handler - INFO - Fetching complete. Success rate: 100.00%
2025-08-09 14:57:21,848 - selene.application.containers.market_data_container - INFO - Closing database connections
```



## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**selene** - Built using Clean Architecture principles
