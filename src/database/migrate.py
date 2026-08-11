"""Migration  runner don gian - versioning schema bang file SQL danh so thu tu

Moi migration la 1 file '.sql' trong 'database/migrations/', dat ten
'NNN_mo_ta.sql' (NNN tang dan). Bang
'schema_migrations' luu lai migration nao da chay, de moi migration chi
duoc ap dung DUNG 1 LAN - chay 'apply_migrations()' nhieu lan tren cung
1 DB (ke ca DB da co du lieu) la an toan (idempotent), chi ap dung phan
migration MOI chua tung chay
"""

from datetime import datetime
from pathlib import Path

from src.database.connection import DatabaseConnection

MIGRATIONS_DIR = Path(__file__).resolve().parents[2] / "database" / "migrations"


def _ensure_migrations_table(db: DatabaseConnection) -> None:
    db.execute_script("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            filename TEXT PRIMARY KEY,
            applied_at TEXT NOT NULL
        );
        """)


def get_applied_migrations(db: DatabaseConnection | None = None) -> set[str]:
    db = db or DatabaseConnection()
    _ensure_migrations_table(db)
    rows = db.fetch_all("SELECT filename FROM schema_migrations;")
    return {row["filename"] for row in rows}


def apply_migrations(db: DatabaseConnection | None = None) -> list[str]:
    """Ap dung moi migration CHUA tung chay, theo dung thu tu ten file.

    Tra ve danh sach ten file vua duoc ap dung trong lan goi nay (rong
    neu DB da co phien ban moi nhat).
    """
    db = db or DatabaseConnection()
    _ensure_migrations_table(db)
    applied = get_applied_migrations(db)

    newly_applied: list[str] = []
    for path in sorted(MIGRATIONS_DIR.glob("*.sql")):
        if path.name in applied:
            continue
        sql = path.read_text(encoding="utf-8")
        db.execute_script(sql)
        db.execute_write(
            "INSERT INTO schema_migrations (filename, applied_at) VALUES (?, ?);",
            (path.name, datetime.utcnow().isoformat()),
            commit=True,
        )
        newly_applied.append(path.name)
    return newly_applied
