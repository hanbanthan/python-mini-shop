from datetime import datetime
from decimal import Decimal

from src.database.connection import DatabaseConnection

class ReportRepository:
    def __init__(self, db: DatabaseConnection | None = None) -> None:
        self._db = db or DatabaseConnection()
    
    @staticmethod
    def _date_filter(
        date_from: datetime | None, date_to: datetime | None, column: str = "created_at"
    ) -> tuple[str, list[object]]:
        clause = ""
        params: list[object] = []
        if date_from is not None:
            clause += f" AND {column} >= ?"
            params.append(date_from.isoformat())
        if date_to is not None:
            clause += f" AND {column} <= ?"
            params.append(date_to.isoformat())
        return clause, params
    
    def count_orders(
        self, date_from: datetime | None = None, date_to: datetime | None = None
    ) -> int:
        clause, params = self._date_filter(date_from, date_to)
        row = self._db.fetch_one(
            f"SELECT COUNT(*) as cnt FROM orders WHERE status = 'completed'{clause}",
            tuple(params),
        )
        return int(row["cnt"]) if row else 0
    
    def revenue_summary(
        self, date_from: datetime | None = None, date_to: datetime | None = None
    ) -> dict[str, Decimal]:
        clause, params = self._date_filter(date_from, date_to)
        row = self._db.fetch_one(
            f"""
            SELECT
                COALESCE(SUM(total_before_discount), 0) AS total_before_discount,
                COALESCE(SUM(discount_amount), 0) AS total_discount,
                COALESCE(SUM(total_amount), 0) AS total_revenue
            FROM orders
            WHERE status = 'completed'{clause}
            """,
            tuple(params),
        )
        return {
            "total_before_discount": Decimal(str(row["total_before_discount"])),
            "total_discount": Decimal(str(row["total_discount"])),
            "total_revenue": Decimal(str(row["total_revenue"])),
        }
    
    def best_selling_products(
        self,
        limit: int = 5,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> list[dict]:
        clause, params = self._date_filter(date_from, date_to, column="o.created_at")
        rows = self._db.fetch_all(
            f"""
            SELECT
                oi.product_id AS product_id,
                oi.product_name_snapshot AS product_name,
                SUM(oi.quantity) AS total_quantity
            FROM order_items oi
            JOIN orders o ON o.id = oi.order_id
            WHERE o.status = 'completed'{clause}
            GROUP BY oi.product_id, oi.product_name_snapshot
            ORDER BY total_quantity DESC
            LIMIT ?
            """,
            (*params, limit),
        )
        return [
            {
                "product_id": row["product_id"],
                "product_name": row["product_name"],
                "total_quantity": int(row["total_quantity"]),
            }
            for row in rows
        ]
    
    def revenue_by_category(
        self, date_from: datetime | None = None, date_to: datetime | None = None
    ) -> dict[str, Decimal]:
        clause, params = self._date_filter(date_from, date_to, column="o.created_at")
        rows = self._db.fetch_all(
            f"""
            SELECT p.category AS category, COALESCE(SUM(oi.subtotal), 0) AS revenue
            FROM order_items oi
            JOIN orders o ON o.id = oi.order_id
            JOIN products p ON p.id = oi.product_id
            WHERE o.status = 'completed'{clause}
            GROUP BY p.category
            ORDER BY revenue DESC
            """,
            tuple(params),
        )
        return {r["category"]: Decimal(str(r["revenue"])) for r in rows}

    def revenue_by_day(
        self, date_from: datetime | None = None, date_to: datetime | None = None
    ) -> dict[str, Decimal]:
        """Doanh thu theo ngày (dựa trên orders.created_at)."""
        clause, params = self._date_filter(date_from, date_to)
        rows = self._db.fetch_all(
            f"""
            SELECT DATE(created_at) AS period, COALESCE(SUM(total_amount), 0) AS revenue
            FROM orders
            WHERE status = 'completed'{clause}
            GROUP BY period
            ORDER BY period
            """,
            tuple(params),
        )
        return {r["period"]: Decimal(str(r["revenue"])) for r in rows}

    
    def revenue_by_month(
        self, date_from: datetime | None = None, date_to: datetime | None = None
    ) -> dict[str, Decimal]:
        clause, params = self._date_filter(date_from, date_to)
        rows = self._db.fetch_all(
            f"""
            SELECT strftime('%Y-%m', created_at) AS period,
                COALESCE(SUM(total_amount), 0) AS revenue
            FROM orders
            WHERE status = 'completed'{clause}
            GROUP BY period
            ORDER BY period
            """,
            tuple(params)
        )
        return {r["period"]: Decimal(str(r["revenue"])) for r in rows}

    def top_orders(
        self, 
        limit: int = 5,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> list[dict]:
        clause, params = self._date_filter(date_from, date_to)
        rows = self._db.fetch_all(
            f"""
            SELECT id, customer_id, total_amount, created_at
            FROM orders
            WHERE status = 'completed'{clause}
            ORDER BY total_amount DESC 
            LIMIT ?
            """,
            (*params, limit),
        )
        return [
            {
                "order_id": row["id"],
                "customer_id": row["customer_id"],
                "total_amount": Decimal(str(row["total_amount"])),
                "created_at": row["created_at"],
            }
            for row in rows
        ]

    def top_customers_by_spending(
        self, 
        limit: int = 5,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> list[dict]:
        clause, params = self._date_filter(date_from, date_to, column="o.created_at")
        rows = self._db.fetch_all(
            f"""
            SELECT c.id AS customer_id, c.full_name AS full_name,
                COALESCE(SUM(o.total_amount), 0) AS total_spent
            FROM customers c
            JOIN orders o ON o.customer_id = c.id
            WHERE o.status = 'completed'{clause}
            GROUP BY c.id, c.full_name
            ORDER BY total_spent DESC
            LIMIT ?
            """,
            (*params, limit),
        )
        return [
            {
                "customer_id": row["customer_id"],
                "full_name": row["full_name"],
                "total_spent": Decimal(str(row["total_spent"])),
            }
            for row in rows
        ]

    