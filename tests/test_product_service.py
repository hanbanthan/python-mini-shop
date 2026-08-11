"""Unit test cho ProductService - dung DB SQLite that, co lap trong tmp_path."""

from decimal import Decimal

import pytest

from src.exceptions import InvalidProductDataError, ProductNotFoundError

def test_add_product_valid(make_product):
    product = make_product(name="Test Product", category="Test Category", price=Decimal("10.00"), stock=5)
    assert product.id is not None
    assert product.name == "Test Product"
    assert product.category == "Test Category"
    assert product.price == Decimal("10.00")
    assert product.stock_quantity == 5
    assert product.is_active is True

def test_add_product_invalid_price_negative(product_service):
    with pytest.raises(InvalidProductDataError):
        product_service.add_product(name="Bad", category="Test", price=Decimal("-1"), stock_quantity=1)

def test_add_product_invalid_price_zero(product_service):
    with pytest.raises(InvalidProductDataError):
        product_service.add_product(name="Bad", category="Test", price=Decimal("0"), stock_quantity=1)
    
def test_add_product_invalid_name_empty(product_service):
    with pytest.raises(InvalidProductDataError):
        product_service.add_product(name=" ", category="Test", price=Decimal("100"), stock_quantity=1)
    
def test_add_product_invalid_stock_negative(product_service):
    with pytest.raises(InvalidProductDataError):
        product_service.add_product(name="Bad", category="Test", price=Decimal("100"), stock_quantity=-1)
    
def test_get_product_found(product_service, make_product):
    product = make_product()
    found = product_service.get_product(product.id)
    assert found.id == product.id
    assert found.name == product.name

def test_get_product_not_found(product_service):
    with pytest.raises(ProductNotFoundError):
        product_service.get_product(999999)

def test_update_stock_valid(product_service, make_product):
    product = make_product(stock=10)
    updated = product_service.update_product(product.id, stock_quantity=25)
    assert updated.stock_quantity == 25
    reloaded = product_service.get_product(product.id)
    assert reloaded.stock_quantity == 25

def test_update_stock_negative_rejected(product_service, make_product):
    product = make_product(stock=10)
    with pytest.raises(InvalidProductDataError):
        product_service.update_product(product.id, stock_quantity=-5)

def test_update_only_changes_given_fields(product_service, make_product):
    product = make_product(name="Original", category="Cat A", price = Decimal("100000"))
    updated = product_service.update_product(product.id, price = Decimal("200000"))
    assert updated.price == Decimal("200000")
    assert updated.name == "Original"
    assert updated.category == "Cat A"

def test_update_product_not_found(product_service):
    with pytest.raises(ProductNotFoundError):
        product_service.update_product(9999999, price = Decimal("100"))
    
def test_search_products_by_keyword_and_price_range(product_service, make_product):
    make_product(name="Ban phim co", category="Electronics", price=Decimal("1000000"))
    make_product(name="Ban phim thuong", category="Electronics", price=Decimal("200000"))
    make_product(name="Ao thun", category="Fashion", price=Decimal("150000"))

    results = product_service.search_products(keyword="ban phim", min_price=Decimal("500000"))
    assert len(results) == 1
    assert results[0].name == "Ban phim co"

def test_search_products_case_insensitive(product_service, make_product):
    make_product(name="Laptop Dell XPS")
    results = product_service.search_products(keyword="LAPTOP dell")
    assert len(results) == 1

def test_remove_product_never_sold_hard_deletes(product_service, make_product):
    product = make_product()
    product_service.remove_product(product.id)
    with pytest.raises(ProductNotFoundError):
        product_service.get_product(product.id)

def test_remove_product_already_sold_deactivates(
    product_service, order_service, make_product, make_customer
): 
    product = make_product(stock=5)
    customer = make_customer()
    order_service.create_order(customer.id, [(product.id, 1)])

    product_service.remove_product(product.id)
    after = product_service.get_product(product.id)
    assert after.is_active is False


