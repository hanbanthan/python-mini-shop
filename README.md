# python-mini-shop

A Python CLI application for managing products, customers, orders, inventory, and revenue reports for a small store. This project is a comprehensive exercise applying OOP, Design Patterns, Database (SQLite), Exception Handling, and Unit Testing.

## Table of Contents

- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Running the Program](#running-the-program)
- [Running Tests](#running-tests)
- [Project Structure](#project-structure)
- [Architecture & Design Patterns](#architecture--design-patterns)
- [Database](#database)
- [Development Tools](#development-tools-linting-formatting--type-checking)
- [Docker](#running-with-docker)

## System Requirements
- python 3.11 or higher
- No separate database server is required - SQLite is built into Python

## Installation
```bash
# 1. Clone / extract the project and move into the project root
cd python-mini-shop

# 2. Create a virtual environment
python3 -m venv venv
source venv/bin/activate # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

The `.evn` file in the project root already contains the default configuration (database path, discount percentage, etc.). You can modify it if needed:

```env
DATABASE_PATH=database/store.db
MAX_DISCOUNT_PERCENT=15
VIP_DISCOUNT_PERCENT=10
LARGE_ORDER_THRESHOLD=5000000
LARGE_ORDER_EXTRA_DISCOUNT=5

```

## Running the API

Start the FastAPI server:

```bash
uvicorn src.api.app:app --reload
```

Then open:

Swagger UI: http://localhost:8000/docs
OpenAPI schema: http://localhost:8000/openapi.json
The API and CLI use the same SQLite database, so data created in one interface is immediately visible in the other

## Running the Program
```bash
python main.py
```

On the first run, the application automatically creates the database file (`database/store.db`) and applies all migrations (table creation). On subsequent runs, the application checks the database version and applies only **NEW** migrations if available, without losing existing data.

To generate sample data for quick testing:

```bash
python -m src.database.seed
```

The program displays the menu and continues running until the user select **"0. Exit"** from the main menu.

## Running Tests

The official test suite is located in `tests/` and is written using `pytest` (53 test cases covering the core business logic):

```bash
pytest -v
```

To measure test coverage:
```bash
pytest --cov=src --cov-report=term-missing
```

> **Note:** The `scripts/` directory contains manual test scripts used during development (`manual_test_*.py`). These are not part of the official grading test suite; they are provided for reference and quick debugging. The `tests/` directory contains the official test suite.

## Project Structure
```text
mini-store-management/
├── main.py                     # Entry point
├── requirements.txt
├── pyproject.toml              # Config for pytest/ruff/black/mypy/coverage
├── .env                        # Configuration (not hard-coded in code)
├── Dockerfile
│
├── database/
│   └── migrations/             # SQL migrations, numbered sequentially (001_, 002_, ...)
│
├── src/
│   ├── config/                  # settings.py (reads .env), logging_config.py
│   ├── exceptions/              # All custom business exceptions
│   ├── models/                  # Product, Customer, Order, OrderItem, Enums
│   ├── database/                # DatabaseConnection (Singleton), init_db, migrate, seed
│   ├── repositories/            # Data access layer (Repository Pattern)
│   ├── patterns/
│   │   ├── discount/             # Strategy + Factory (discount policies)
│   │   └── observer/             # Observer Pattern (order creation events)
│   ├── services/                # Business logic layer
│   └── cli/                     # Command-line interface / menu
│
├── scripts/                      # Manual test scripts used during development
└── tests/                        # Official pytest test suite
```

## Architecture & Design Patterns

The code is clearly separated into layers, with each layer calling only the layer directly below it:

```text
CLI -> Service -> Repository -> Database (SQLite)
```

** 4 main Design Pattens, each solving a real problem:**
| Pattern | Location | Problem Solved |
|---|---|---|
| **Singleton** | `src/database/connection.py` | Allows all repositories to share the same connection so transactions across multiple tables work correctly |
| **Repository** | `src/repositories/` | Seperates data access from business logic; Services do not write SQL |
| **Strategy** | `src/patterns/discount/` | Provides different policies based on customer type and allows the policy to be changed at run time |
| **Factory** | `src/patterns/discount/factory.py` | Selects the correct Strategy based on `CustomerType` without spreading `if/elif` logic through the code |
| **Observer** *(advanced)* | `src/patterns/observer/` | After an order is created, publishes an event for additional tasks such as inventory logging, customer notifications, or audit logging, while keeping those tasks independent from the order-creation logic |

## Database

The application uses SQLite with a simple **migration-based versioning mechanism** (`src/database/migrate.py`). Each `.sql` file in `database/migrations/` is numbered sequentially and is executed exactly once. The `schema_migrations` table keeps track of which migrations have already been applied. Therefore, running:

```bash
python -m src.database.init_db
```

multiple times is safe.

** 4 business tables: **
- `products`
- `customers`
- `orders`
- `order_items`

See the detailed schema in `database/migrations/001_init.sql`.

There is also an `audit_log` table, created by migration `002`,
which stores queryable audit log records.

### Safety
- All queries use parameterized SQL (`?` placeholders); user input is never concatenated directly into SQL.
- Order creation is atomic - everything is committed once and the the entire transaction is rolled back if an error occurs.
- Stock deduction uses `UPDATE ... WHERE stock_quantity >= ?` (conditional update) to remain safe when multiple transactions attempt to purchase the same product at nearly the same time - preventing the system from selling more items than are actually in stock, even under a race condition.

## Development Tools (Linting / Formatting / Type Checking)

The following tools are configured in `pyproject.toml`:

```bash
black .       # Format code
ruff check .  # Lint code
mypy src      # Static type checking
```

## Running with Docker

```bash
docker build -t mini-store
docker run -it --rm -v "$(pwd)/database:/app/database" mini-store
```

The `database/` directory is mounted outside the container so that database data is preserved when the container is removed.
