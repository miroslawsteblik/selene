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

The project follows **Clean Architecture** and **Hexagonal Architecture** patterns:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Adapters      │    │   Application   │    │     Domain      │
│   (External)    │    │   (Use Cases)   │    │  (Business)     │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • CLI Handler   │    │ • Use Cases     │    │ • Entities      │
│ • API Clients   │◄───┤ • Containers    │◄───┤ • Services      │
│ • Repositories  │    │ • Orchestration │    │ • Value Objects │
│ • Data Mappers  │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         ▲                       ▲                       ▲
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Infrastructure  │    │      Ports      │    │   Configuration │
│                 │    │  (Interfaces)   │    │                 │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • Database      │    │ • Repository    │    │ • Config Loader │
│ • Logging       │    │ • API Ports     │    │ • Env Variables │
│ • Connection    │    │ • Service Ports │    │ • Validation    │
│   Management    │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

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
- **Repositories**: Data persistence implementations
- **APIs**: External service integrations (`AlphaVantageAPI`)
- **Mappers**: Data transformation between layers

#### 4. **Infrastructure Layer** (`infrastructure/`)

- **Database**: Connection management and pooling
- **Configuration**: Environment-aware config loading
- **Logging**: Comprehensive logging with emoji-safe formatting

#### 5. **Ports** (`ports/`)

- **Interfaces**: Abstract contracts between layers
- **Repository Ports**: Data access interfaces
- **Service Ports**: External service interfaces

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
   git clone <repository-url>
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
   # config/fetch_api.yaml
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
selene fetch --config config/fetch_api.yaml

# Verbose logging
selene fetch --config config/fetch_api.yaml --verbose

# Quiet mode
selene fetch --config config/fetch_api.yaml --quiet
```

#### Configuration

The system uses a two-tier configuration approach:

1. **YAML Configuration** (`config/fetch_api.yaml`):

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

## 📊 Architecture Highlights

### Dependency Injection

```python
# Container manages all dependencies
container = MarketDataContainer(config_path)
use_case = container.create_use_case()
result = use_case.execute(symbols)
```

### Clean Separation of Concerns

```python
# Domain Service (business logic)
class MarketDataService:
    def fetch_and_store_market_data(self, symbols: List[str]) -> Dict[str, Any]

# Use Case (application logic)
class FetchMarketDataUseCase:
    def execute(self, symbols: List[str]) -> Dict[str, Any]

# Adapter (infrastructure)
class AlphaVantageAPI:
    def get_market_data(self, symbol: str) -> APIResponse
```

### Repository Pattern

```python
# Port (interface)
class MarketDataRepositoryPort:
    def save(self, market_data: MarketData) -> MarketData

# Adapter (implementation)
class PostgresMarketDataRepository(MarketDataRepositoryPort):
    def save(self, market_data: MarketData) -> MarketData
```

## 🛡️ Quality Assurance

### Code Quality Tools

- **Black**: Code formatting
- **isort**: Import sorting
- **Pylint**: Static analysis
- **MyPy**: Type checking
- **Pytest**: Unit testing

### Configuration

```toml
# pyproject.toml
[tool.black]
line-length = 88

[tool.pylint]
max-line-length = 88
disable = ["C0111", "C0103", "R0903", "E1101", "E0611"]

[tool.mypy]
strict_equality = true
ignore_missing_imports = true
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
$ selene fetch --config config/fetch_api.yaml --verbose

2025-08-09 14:57:20,588 - selene.application.containers.market_data_container - INFO - Configuration loaded successfully
2025-08-09 14:57:20,588 - selene.infrastructure.database.connection_factory - INFO - Initializing PostgreSQL connection pool: 1-10 connections
2025-08-09 14:57:20,597 - selene.infrastructure.database.connection_factory - INFO - Connected to PostgreSQL: PostgreSQL 16.9 (Ubuntu 16.9-0ubuntu0.24.04.1)
2025-08-09 14:57:20,597 - selene.infrastructure.database.connection_factory - INFO - PostgreSQL connection pool initialized successfully
2025-08-09 14:57:21,848 - selene.adapters.cli.cli_handler - INFO - Fetching complete. Success rate: 100.00%
2025-08-09 14:57:21,848 - selene.application.containers.market_data_container - INFO - Closing database connections
```

## 📋 Project Structure

```
selene/
├── adapters/           # External interfaces
│   ├── cli/           # Command-line interface
│   ├── repository/    # Data persistence
│   └── service/       # External services
├── application/       # Use cases and orchestration
│   ├── containers/    # Dependency injection
│   └── use_cases/     # Application logic
├── domains/           # Business logic
│   └── market_data/   # Market data domain
├── infrastructure/    # Cross-cutting concerns
│   ├── configuration/ # Config management
│   ├── database/      # Database infrastructure
│   └── logging/       # Logging system
├── ports/             # Interfaces/contracts
│   └── market_data/   # Domain ports
├── config/            # Configuration files
├── logs/              # Log files (auto-created)
└── main.py            # Application entry point
```

## 🤝 Contributing

1. Follow the existing architecture patterns
2. Maintain clean separation between layers
3. Add comprehensive logging to new features
4. Include type hints for all public APIs
5. Write tests for business logic
6. Update documentation for architectural changes

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**selene** - Built using Clean Architecture principles
