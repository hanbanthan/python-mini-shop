"""
Script to initialize the database 

Run python src/database/init_db.py 
"""

from pathlib import Path

from src.config.settings import settings
from src.database.connection import DatabaseConnection

# Point to the database/migrations/001_init.sql file 
SCHEMA_PATH = Path(__file__).resolve().parents[2] / "database" / "migrations" / "001_init.sql"

def init_db() -> None:
    Path (settings.database_path).parent.mkdir(parents=True, exist_ok=True)

    schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
    db = DatabaseConnection()
    db.execute_script(schema_sql)

    print(f"Database initialized at: {settings.database_path}")
    print("Tables created: products, customers, orders, order_items")

if __name__ == "__main__":
    init_db()