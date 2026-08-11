"""AuditLogRepository - luu audit log duoi dang DB, bo sung (khong thay the)
cho file `logs/audit.log` o giai doan 7. Co bang DB giup audit log truy van duoc
(vi du: liet ke audit log cua don hang 5) thay vi chi doc file text tuan tu
"""

from datetime import datetime

from src.database.connection import DatabaseConnection


class AuditLogRepository:
    def __init__(self, db: DatabaseConnection | None = None) -> None:
        self._db = db or DatabaseConnection()

    def add_entry(
        self,
        event_type: str,
        details: str,
        order_id: int | None = None,
        customer_id: int | None = None,
    ) -> None:
        self._db.execute_write(
            """
            INSERT INTO audit_log (event_type, details, order_id, customer_id, created_at)
            VALUES (?, ?, ?, ?, ?);
            """,
            (event_type, details, order_id, customer_id, datetime.utcnow().isoformat()),
            commit=True,
        )

    def get_all(self, limit: int = 100) -> list[dict]:
        rows = self._db.fetch_all("SELECT * FROM audit_log ORDER BY id DESC LIMIT ?;", (limit,))
        return [dict(row) for row in rows]

    def get_by_order_id(self, order_id: int) -> list[dict]:
        rows = self._db.fetch_all(
            "SELECT * FROM audit_log WHERE order_id = ? ORDER BY id", (order_id,)
        )
        return [dict(row) for row in rows]
