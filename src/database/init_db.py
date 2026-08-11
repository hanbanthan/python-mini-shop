"""
Script to initialize the database

Run python src/database/init_db.py
"""

from pathlib import Path

from src.config.settings import settings
from src.database.connection import DatabaseConnection
from src.database.migrate import apply_migrations


def init_db() -> None:
    Path(settings.database_path).parent.mkdir(parents=True, exist_ok=True)

    db = DatabaseConnection()
    newly_applied = apply_migrations(db)

    if newly_applied:
        print(f"Database initialized and {len(newly_applied)} migrations applied.")
        print(f"List of applied migrations: {newly_applied}")
    else:
        print("Database already initialized. No new migrations applied.")


if __name__ == "__main__":
    init_db()
