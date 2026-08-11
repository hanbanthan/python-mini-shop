"""
ProductRepository - Repository pattern for Product entity

Take reponse from switching between object Product in Python and
table products in SQlite. This is only the place allow to write
SQL queries, ProductService can not query DB directly
"""

import sqlite3
from datetime import datetime
from decimal import Decimal

from src.database.connection import DatabaseConnection
from src.exceptions import DatabaseOperationError, ProductNotFoundError
from src.models.enums import ProductStatus
from src.models.product import Product
from src.repositories.base_repository import BaseRepository


class ProductRepository(BaseRepository[Product]):
    def __init__(self, db: DatabaseConnection | None = None) -> None:
        # Constructor injection: allow to pass falke/mock DB when unit test
        # default use Singleton DatabaseConnection instance
        self._db = db or DatabaseConnection()

    def add(self, product: Product) -> Product:
        try:
            new_id = self._db.execute_write(
                """
                INSERT INTO products
                    (name, category, price, stock_quantity, tags, is_active, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    product.name,
                    product.category,
                    str(product.price),
                    product.stock_quantity,
                    ",".join(sorted(product.tags)),
                    1 if product.is_active else 0,
                    product.created_at.isoformat(),
                    product.updated_at.isoformat(),
                ),
            )
        except DatabaseOperationError:
            raise

        except sqlite3.Error as exc:
            raise DatabaseOperationError("Failed to add product: {exc}") from exc
        product.id = new_id
        return product

    def get_by_id(self, entity_id: int) -> Product | None:
        row = self._db.fetch_one("SELECT * FROM products WHERE id = ?", (entity_id,))
        return self._row_to_product(row) if row else None

    def get_by_id_or_raise(self, entity_id: int) -> Product:
        product = self.get_by_id(entity_id)
        if product is None:
            raise ProductNotFoundError(f"Product with id {entity_id} not found")
        return product

    def get_all(self) -> list[Product]:
        rows = self._db.fetch_all("SELECT * FROM products")
        return [self._row_to_product(row) for row in rows]

    def get_page(self, page: int = 1, page_size: int = 10) -> tuple[list[Product], int]:
        """(Nang cao) Phan trang bang LIMIT/OFFSET ngay tai DB - khac voi
        cach phan trang phia client (`io_helpers.paginate`) dang load het
        roi cat trong bo nho. Cach nay chi doc dung `page_size` dong can
        thiet tu DB, phu hop khi so luong san pham lon.

        Tra ve (danh sach san pham trong trang, tong so san pham)
        """
        if page < 1:
            page = 1
        offset = (page - 1) * page_size
        rows = self._db.fetch_all(
            "SELECT * FROM products ORDER BY id LIMIT ? OFFSET ?", (page_size, offset)
        )
        total_row = self._db.fetch_one("SELECT COUNT(*) as cnt FROM products")
        total = int(total_row["cnt"]) if total_row is not None else 0
        return [self._row_to_product(row) for row in rows], total

    def search(
        self,
        keyword: str | None = None,
        category: str | None = None,
        active_only: bool | None = False,
    ) -> list[Product]:
        query = "SELECT * FROM products WHERE 1=1"
        params: list[object] = []
        if keyword:
            query += " AND LOWER(name) LIKE ?"
            params.append(f"%{keyword.lower()}%")
        if category:
            query += " AND category = ?"
            params.append(category)
        if active_only:
            query += " AND is_active = 1"
        query += " ORDER BY id"
        rows = self._db.fetch_all(query, tuple(params))
        return [self._row_to_product(row) for row in rows]

    def update(self, product: Product) -> None:
        if product.id is None:
            raise ProductNotFoundError("Product id is required")
        self._db.execute_write(
            """
            UPDATE products
            SET name = ?, category = ?, price = ?, stock_quantity = ?, tags = ?, is_active = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                product.name,
                product.category,
                str(product.price),
                product.stock_quantity,
                ",".join(product.tags),
                1 if product.is_active else 0,
                product.updated_at.isoformat(),
                product.id,
            ),
        )

    def deactivate(self, entity_id: int) -> None:
        product = self.get_by_id_or_raise(entity_id)
        product.deactivate()
        self.update(product)

    def has_been_sold(self, entity_id: int) -> bool:
        row = self._db.fetch_one(
            "SELECT COUNT(*) as cnt FROM order_items WHERE product_id = ?", (entity_id,)
        )
        return bool(row and row["cnt"] > 0)

    def delete_hard(self, entity_id: int) -> None:
        self._db.execute_write("DELETE FROM products WHERE id = ?", (entity_id,))

    @staticmethod
    def _row_to_product(row: sqlite3.Row) -> Product:
        """map sqlite3.Row -> object Product, convert datat correctly:
        tags(string "a,b,c") -> set[str], is_active(0/1) -> ProductStatus,
        price(NUMERIC) -> Decimal.
        """
        tags = set(row["tags"].split(",")) if row["tags"] else set()
        product = Product(
            id=row["id"],
            name=row["name"],
            category=row["category"],
            price=Decimal(row["price"]),
            tags=tags,
            status=ProductStatus.ACTIVE if row["is_active"] else ProductStatus.INACTIVE,
        )
        # this is rehydrate of Reposiotry, data is validate
        # when write to DB, so we do not need to reduce_stock()
        # or increase_stock()
        product._stock_quantity = row["stock_quantity"]
        product.created_at = datetime.fromisoformat(row["created_at"])
        product.updated_at = datetime.fromisoformat(row["updated_at"])
        return product
