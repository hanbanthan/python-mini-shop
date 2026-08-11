"""
Script to add data to database to test or develop the application

Run python -m src.database.seed
NOTE: Only run this script after running init_db.py
"""

from datetime import datetime

from src.database.connection import DatabaseConnection


def seed() -> None:
    db = DatabaseConnection()
    now = datetime.now().isoformat()

    products = [
        ("Laptop Dell XPS 13", "Electronics", 25000000, 10, "laptop,dell,hot", 1, now, now),
        ("Chuot khong day Logitech", "Electronics", 350000, 50, "mouse,logitech", 1, now, now),
        ("Ao thun basic", "Fashion", 150000, 100, "clothing,basic", 1, now, now),
        ("Ban phim co", "Electronics", 1200000, 20, "keyboard,mechanical", 1, now, now),
    ]

    db.execute_many(
        """
        INSERT INTO products
        (name, category, price, stock_quantity, tags, is_active, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        products,
    )

    customers = [
        ("Nguyen Van A", "vana@example.com", "0901234567", "vip", now, now),
        ("Tran Thi B", "tranb@example.com", "0912345678", "regular", now, now),
    ]

    db.execute_many(
        """
        INSERT INTO customers
        (full_name, email, phone, customer_type, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        customers,
    )

    print(f"Seeded database with {len(products)} products and {len(customers)} customers.")


if __name__ == "__main__":
    seed()
