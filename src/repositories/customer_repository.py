import sqlite3
from datetime import datetime

from src.database.connection import DatabaseConnection
from src.exceptions import CustomerNotFoundError, DatabaseOperationError, InvalidCustomerDataError
from src.models.customer import Customer
from src.models.enums import CustomerType
from src.repositories.base_repository import BaseRepository


class CustomerRepository(BaseRepository[Customer]):
    def __init__(self, db: DatabaseConnection | None = None) -> None:
        self._db = db or DatabaseConnection()

    def add(self, customer: Customer) -> Customer:
        try:
            new_id = self._db.execute_write(
                """
                INSERT INTO customers
                (full_name, email, phone, customer_type, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    customer.full_name,
                    customer.email,
                    customer.phone,
                    customer.customer_type.value,
                    customer.created_at.isoformat(),
                    customer.updated_at.isoformat(),
                ),
            )
        except DatabaseOperationError as exc:
            if "UNIQUE" in str(exc):
                raise InvalidCustomerDataError(f"Email {customer.email} already exists.") from exc
            raise
        customer.id = new_id
        return customer

    def get_by_id(self, entity_id: int) -> Customer | None:
        row = self._db.fetch_one("SELECT * FROM customers WHERE id = ?", (entity_id,))
        return self._row_to_customer(row) if row else None

    def get_by_id_or_raise(self, entity_id: int) -> Customer:
        customer = self.get_by_id(entity_id)
        if customer is None:
            raise CustomerNotFoundError(f"Customer with id {entity_id} not found")
        return customer

    def get_by_email(self, email: str) -> Customer | None:
        row = self._db.fetch_one("SELECT * FROM customers WHERE email = ?", (email,))
        return self._row_to_customer(row) if row else None

    def get_all(self) -> list[Customer]:
        rows = self._db.fetch_all("SELECT * FROM customers")
        return [self._row_to_customer(row) for row in rows]

    def search(self, keyword: str | None = None) -> list[Customer]:
        query = "SELECT * FROM customers WHERE 1=1"
        params: list[object] = []
        if keyword:
            query += " AND (LOWER(full_name) LIKE ? OR LOWER(email) LIKE ?)"
            like = f"%{keyword.lower()}%"
            params.extend([like, like])
        query += " ORDER BY id"
        rows = self._db.fetch_all(query, tuple(params))
        return [self._row_to_customer(row) for row in rows]

    def update(self, customer: Customer) -> None:
        if customer.id is None:
            raise CustomerNotFoundError("Customer id is required ")
        try:
            self._db.execute_write(
                """
                UPDATE customers
                SET full_name = ?, email = ?, phone = ?, customer_type = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    customer.full_name,
                    customer.email,
                    customer.phone,
                    customer.customer_type.value,
                    customer.updated_at.isoformat(),
                    customer.id,
                ),
            )
        except DatabaseOperationError as exc:
            if "UNIQUE" in str(exc):
                raise InvalidCustomerDataError(f"Email {customer.email} already exists.") from exc
            raise

    def has_orders(self, entity_id: int) -> bool:
        row = self._db.fetch_one(
            "SELECT COUNT(*) AS cnt FROM orders WHERE customer_id = ?", (entity_id,)
        )
        return bool(row and row["cnt"] > 0)

    def delete(self, entity_id: int) -> None:
        self._db.execute_write("DELETE FROM customers WHERE id = ?", (entity_id,))

    @staticmethod
    def _row_to_customer(row: sqlite3.Row) -> Customer:
        return Customer(
            id=row["id"],
            full_name=row["full_name"],
            email=row["email"],
            phone=row["phone"],
            customer_type=CustomerType(row["customer_type"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )
