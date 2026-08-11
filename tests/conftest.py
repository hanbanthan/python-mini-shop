"""Fixture dùng chung cho toàn bộ test suite.

Nguyên tắc: MỖI test function chạy trên 1 file SQLite RIÊNG trong
tmp_path (pytest tự tạo và tự xóa) — hoàn toàn cô lập với DB thật của
ứng dụng (`database/store.db`) và cô lập giữa các test với nhau.

Vì DatabaseConnection là Singleton, fixture `test_db` phải RESET lại
_instance/_connection trước và sau mỗi test để đảm bảo mỗi test luôn
lấy được 1 connection MỚI trỏ đúng vào DB tạm của chính nó, không bị
dính connection cũ từ test trước.
"""

from decimal import Decimal
from pathlib import Path

import pytest

import src.database.connection as connection_module
from src.config.settings import Settings
from src.database.migrate import apply_migrations
from src.models.enums import CustomerType
from src.patterns.observer.publisher import OrderEventPublisher
from src.services.customer_service import CustomerService
from src.services.order_service import OrderService
from src.services.product_service import ProductService
from src.services.report_service import ReportService

PROJECT_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture()
def test_db(tmp_path, monkeypatch):
    """DB SQLite thật, riêng cho từng test, tự áp dụng migration, tự dọn dẹp."""
    db_path = tmp_path / "test_store.db"
    test_settings = Settings(database_path=str(db_path))
    # Patch đúng cái tên `settings` mà connection.py đang dùng (không phải
    # patch src.config.settings.settings, vì connection.py đã import
    # binding riêng lúc module load).
    monkeypatch.setattr(connection_module, "settings", test_settings)

    connection_module.DatabaseConnection._instance = None
    connection_module.DatabaseConnection._connection = None

    db = connection_module.DatabaseConnection()
    apply_migrations(db)

    yield db

    db.close()
    connection_module.DatabaseConnection._instance = None
    connection_module.DatabaseConnection._connection = None


@pytest.fixture()
def product_service(test_db) -> ProductService:
    return ProductService()


@pytest.fixture()
def customer_service(test_db) -> CustomerService:
    return CustomerService()


@pytest.fixture()
def order_service(test_db) -> OrderService:
    # Publisher rỗng (khong observer nao) -> test gon gang, khong in log/
    # ghi audit.log thật ra ổ đĩa của máy chạy test.
    return OrderService(order_event_publisher=OrderEventPublisher())


@pytest.fixture()
def report_service(test_db) -> ReportService:
    return ReportService()


@pytest.fixture()
def make_product(product_service):
    """Factory tạo nhanh 1 Product hợp lệ cho test, có thể override từng field."""

    def _make(
        name: str = "Test Product",
        category: str = "Test",
        price: Decimal = Decimal("100000"),
        stock: int = 10,
        tags: set[str] | None = None,
    ):
        return product_service.add_product(
            name=name, category=category, price=price, stock_quantity=stock, tags=tags
        )

    return _make


@pytest.fixture()
def make_customer(customer_service):
    """Factory tạo nhanh 1 Customer hợp lệ cho test — tự sinh email không
    trùng nếu không truyền vào."""
    counter = {"n": 0}

    def _make(
        full_name: str = "Test Customer",
        email: str | None = None,
        phone: str = "0900000000",
        customer_type: CustomerType = CustomerType.REGULAR,
    ):
        counter["n"] += 1
        if email is None:
            email = f"test.customer.{counter['n']}@example.com"
        return customer_service.add_customer(
            full_name=full_name, email=email, phone=phone, customer_type=customer_type
        )

    return _make
