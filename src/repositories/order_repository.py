"""
add() create order go with all order items
in 1 transaction - atomic, only 1 commit, rollback
if any error occurs
"""

import sqlite3
from datetime import datetime
from decimal import Decimal

from src.database.connection import DatabaseConnection
from src.exceptions import InsufficientStockError, InvalidOrderError, OrderNotFoundError
from src.models.enums import OrderStatus
from src.models.order import Order
from src.models.order_item import OrderItem
from src.repositories.base_repository import BaseRepository


class OrderRepository(BaseRepository[Order]):
    def __init__(self, db: DatabaseConnection | None = None) -> None:
        self._db = db or DatabaseConnection()

    def add(self, order: Order) -> Order:
        order.validate_not_empty()
        with self._db.transaction() as cursor:
            cursor.execute(
                """
                INSERT INTO orders
                (customer_id, total_before_discount, discount_amount, total_amount,
                status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    order.customer_id,
                    str(order.total_before_discount),
                    str(order.discount_amount),
                    str(order.total_amount),
                    order.status.value,
                    order.created_at.isoformat(),
                    order.updated_at.isoformat(),
                ),
            )
            order_id = cursor.lastrowid
            for item in order.items:
                cursor.execute(
                    """
                    INSERT INTO order_items
                    (order_id, product_id, product_name_snapshot, quantity,
                    unit_price_snapshot, subtotal)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        order_id,
                        item.product_id,
                        item.product_name_snapshot,
                        item.quantity,
                        str(item.unit_price_snapshot),
                        str(item.subtotal),
                    ),
                )

        order.id = order_id
        return order

    def create_order_with_stock_update(
        self, order: Order, stock_deductions: dict[int, int]
    ) -> Order:
        order.validate_not_empty()
        with self._db.transaction() as cursor:
            cursor.execute(
                """
                INSERT INTO orders
                (customer_id, total_before_discount, discount_amount, total_amount,
                status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    order.customer_id,
                    str(order.total_before_discount),
                    str(order.discount_amount),
                    str(order.total_amount),
                    order.status.value,
                    order.created_at.isoformat(),
                    order.updated_at.isoformat(),
                ),
            )
            order_id = cursor.lastrowid

            for item in order.items:
                cursor.execute(
                    """
                    INSERT INTO order_items
                    (order_id, product_id, product_name_snapshot, quantity,
                    unit_price_snapshot, subtotal)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        order_id,
                        item.product_id,
                        item.product_name_snapshot,
                        item.quantity,
                        str(item.unit_price_snapshot),
                        str(item.subtotal),
                    ),
                )

            now_iso = datetime.now().isoformat()
            for product_id, quantity in stock_deductions.items():
                cursor.execute(
                    """
                    UPDATE products
                    SET stock_quantity = stock_quantity - ?, updated_at = ?
                    WHERE id = ? AND stock_quantity >= ?
                    """,
                    (quantity, now_iso, product_id, quantity),
                )
                if cursor.rowcount == 0:
                    raise InsufficientStockError(f"Insufficient stock for product id {product_id}")

        order.id = order_id
        return order

    def cancel_order_with_stock_update(
        self, order: Order, stock_deductions: dict[int, int]
    ) -> Order:
        if order.id is None:
            raise InvalidOrderError("Order id is required for canceling")

        with self._db.transaction() as cursor:
            cursor.execute(
                """
                UPDATE orders
                SET status = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    order.status.value,
                    order.updated_at.isoformat(),
                    order.id,
                ),
            )

            now_iso = datetime.now().isoformat()

            for product_id, new_stock in stock_deductions.items():
                cursor.execute(
                    "UPDATE products SET stock_quantity = ?, updated_at = ? WHERE id = ?",
                    (new_stock, now_iso, product_id),
                )

        return order

    def get_by_id(self, entity_id: int) -> Order | None:
        order_row = self._db.fetch_one("SELECT * FROM orders WHERE id = ?", (entity_id,))
        if order_row is None:
            return None
        return self._load_order(order_row)

    def get_by_id_or_raise(self, entity_id: int) -> Order:
        order = self.get_by_id(entity_id)
        if order is None:
            raise OrderNotFoundError(f"Order with id {entity_id} not found")
        return order

    def get_all(self) -> list[Order]:
        order_rows = self._db.fetch_all("SELECT * FROM orders ORDER BY id")
        return [self._load_order(row) for row in order_rows]

    def get_page(self, page: int = 1, page_size: int = 10) -> tuple[list[Order], int]:
        """Nang cao, phan trang bang LIMIT/OFFSET ngay tai DB."""
        if page < 1:
            page = 1
        offset = (page - 1) * page_size
        order_rows = self._db.fetch_all(
            "SELECT * FROM orders ORDER BY id LIMIT ? OFFSET ?", (page_size, offset)
        )
        total_row = self._db.fetch_one("SELECT COUNT(*) as total FROM orders")
        total = int(total_row["total"]) if total_row is not None else 0
        return [self._load_order(row) for row in order_rows], total

    def search(
        self,
        customer_id: int | None = None,
        status: OrderStatus | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> list[Order]:
        query = "SELECT * FROM orders WHERE 1=1"
        params: list[object] = []
        if customer_id is not None:
            query += " AND customer_id = ?"
            params.append(customer_id)
        if status is not None:
            query += " AND status = ?"
            params.append(status.value)
        if date_from is not None:
            query += " AND created_at >= ?"
            params.append(date_from.isoformat())
        if date_to is not None:
            query += " AND created_at <= ?"
            params.append(date_to.isoformat())
        query += " ORDER BY id"

        order_rows = self._db.fetch_all(query, tuple(params))
        return [self._load_order(row) for row in order_rows]

    def update(self, order: Order) -> None:
        if order.id is None:
            raise InvalidOrderError("Order id is required for updated")
        self._db.execute_write(
            """
            UPDATE orders
            SET total_before_discount = ?, discount_amount = ?, total_amount = ?,
            status = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                str(order.total_before_discount),
                str(order.discount_amount),
                str(order.total_amount),
                order.status.value,
                order.updated_at.isoformat(),
                order.id,
            ),
        )

    def _load_order(self, order_row: sqlite3.Row) -> Order:
        item_rows = self._db.fetch_all(
            "SELECT * FROM order_items WHERE order_id = ? ORDER BY id",
            (order_row["id"],),
        )
        return self._row_to_order(order_row, item_rows)

    @staticmethod
    def _row_to_order(order_row: sqlite3.Row, items_rows: list[sqlite3.Row]) -> Order:
        order = Order(
            id=order_row["id"],
            customer_id=order_row["customer_id"],
        )

        for item_row in items_rows:
            order.add_item(
                OrderItem(
                    product_id=item_row["product_id"],
                    product_name_snapshot=item_row["product_name_snapshot"],
                    quantity=item_row["quantity"],
                    unit_price_snapshot=Decimal(str(item_row["unit_price_snapshot"])),
                )
            )

        discount = Decimal(str(order_row["discount_amount"]))
        if discount > 0:
            order.apply_discount(discount)

        order.status = OrderStatus(order_row["status"])
        order.created_at = datetime.fromisoformat(order_row["created_at"])
        order.updated_at = datetime.fromisoformat(order_row["updated_at"])
        return order
