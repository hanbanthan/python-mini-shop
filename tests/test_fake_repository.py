""" Unit test cho ProductService dung FAKE repository - khong cham DB that.

Chung minh Repository patten hoat dong dung: ProductService chi phu
thuoc vao interface BaseRepository (qua constructor injection), co the
thay bang bat ki implementation nao - ke ca 1 fake repository chay hoan 
toan trong bo nho, khong can SQLite. Day cung la cach test
"loi database (mock)" ma khong can that su lam hong ket noi DB.
"""

from decimal import Decimal

import pytest

from src.exceptions import DatabaseOperationError, ProductNotFoundError
from src.models.product import Product
from src.repositories.base_repository import BaseRepository
from src.services.product_service import ProductService

class FakeProductRepository(BaseRepository[Product]):
    """Repository gia lap - luu Product trong dict thay vi SQLite."""

    def __init__(self) -> None:
        self._data: dict[int, Product] = {}
        self._next_id = 1
        self.raise_db_error_on_add = False
    
    def add(self, product: Product) -> Product:
        if self.raise_db_error_on_add:
            raise DatabaseOperationError("Gia lap loi ket noi database")
        product.id = self._next_id
        self._data[self._next_id] = product
        self._next_id += 1
        return product
    
    def get_by_id(self, entity_id: int) -> Product | None:
        return self._data.get(entity_id)
    
    def get_by_id_or_raise(self, entity_id: int) -> Product:
        product = self.get_by_id(entity_id)
        if product is None:
            raise ProductNotFoundError(f"Product with ID {entity_id} not found")
        return product
    
    def get_all(self) -> list[Product]:
        return list(self._data.values())
    
    def search(self, keyword=None, category=None, active_only=False) -> list[Product]:
        results = list(self._data.values())
        if keyword:
            results = [p for p in results if keyword.lower() in p.name.lower()]
        if category:
            results = [p for p in results if p.category == category]
        if active_only:
            results = [p for p in results if p.is_active]
        return results
    
    def update(self, product: Product) -> None:
        self._data[product.id] = product
    
    def deactivate(self, entity_id: int) -> None:
        product = self.get_by_id_or_raise(entity_id)
        product.deactivate()
    
    def has_been_sold(self, entity_id: int) -> bool:
        return False
    
    def delete_hard(self, entity_id: int) -> None:
        self._data.pop(entity_id, None)
    
def test_product_service_with_fake_repository_add_and_get():
    fake_repo = FakeProductRepository()
    service = ProductService(product_repository=fake_repo)

    product = service.add_product(
        name="Fake Product", category="Test", price=Decimal("100000"), stock_quantity=5
    )

    assert product.id == 1
    fetched = service.get_product(product.id)
    assert fetched.name == "Fake Product"
    assert fetched.stock_quantity == 5

def test_product_service_with_fake_repository_not_found():
    fake_repo = FakeProductRepository()
    service = ProductService(product_repository=fake_repo)

    with pytest.raises(ProductNotFoundError):
        service.get_product(999)

def test_product_service_propagates_database_error():
    fake_repo = FakeProductRepository()
    fake_repo.raise_db_error_on_add = True
    service = ProductService(product_repository=fake_repo)

    with pytest.raises(DatabaseOperationError):
        service.add_product(
            name="Fake Product", category="Test", price=Decimal("100"), stock_quantity=1
        )

def test_product_service_search_with_fake_repository():
    fake_repo = FakeProductRepository()
    service = ProductService(product_repository=fake_repo)
    service.add_product(name="Laptop Dell", category="Electronics", price=Decimal("1000000"), stock_quantity=1)
    service.add_product(name="Ao thun", category="Fashion", price=Decimal("100000"), stock_quantity=1)

    results = service.search_products(category="Electronics")
    assert len(results) == 1
    assert results[0].name == "Laptop Dell"