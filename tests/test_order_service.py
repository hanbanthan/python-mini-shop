from decimal import Decimal

<<<<<<< HEAD
import pytest 

from src.exceptions import CustomerNotFoundError, InsufficientStockError, InvalidOrderError
from src.models.enums import CustomerType, OrderStatus
=======
import pytest

from src.exceptions import CustomerNotFoundError, InsufficientStockError, InvalidOrderError
from src.models.enums import OrderStatus

>>>>>>> origin/main

def test_create_order_success(order_service, make_customer, make_product):
    customer = make_customer()
    product = make_product(price=Decimal("500000"), stock=10)

    order = order_service.create_order(customer.id, [(product.id, 2)])

    assert order.id is not None
    assert order.total_before_discount == Decimal("1000000")
    assert order.total_amount == Decimal("1000000")
    assert order.status == OrderStatus.COMPLETED

<<<<<<< HEAD
=======

>>>>>>> origin/main
def test_create_order_multiple_products(order_service, make_customer, make_product):
    customer = make_customer()
    p1 = make_product(name="San pham A", price=Decimal("100000"), stock=10)
    p2 = make_product(name="San pham B", price=Decimal("200000"), stock=10)

    order = order_service.create_order(customer.id, [(p1.id, 2), (p2.id, 3)])

    assert len(order.items) == 2
    assert order.total_before_discount == Decimal("800000")

<<<<<<< HEAD
=======

>>>>>>> origin/main
def test_create_order_empty_items_rejected(order_service, make_customer):
    customer = make_customer()
    with pytest.raises(InvalidOrderError):
        order_service.create_order(customer.id, [])

<<<<<<< HEAD
=======

>>>>>>> origin/main
def test_create_order_insufficient_stock_rejected(order_service, make_customer, make_product):
    customer = make_customer()
    product = make_product(stock=2)
    with pytest.raises(InsufficientStockError):
        order_service.create_order(customer.id, [(product.id, 100)])

<<<<<<< HEAD
=======

>>>>>>> origin/main
def test_create_order_not_found(order_service, make_product):
    product = make_product()
    with pytest.raises(CustomerNotFoundError):
        order_service.create_order(999999, [(product.id, 1)])

<<<<<<< HEAD
=======

>>>>>>> origin/main
def test_create_order_zero_quantity_rejected(order_service, make_customer, make_product):
    customer = make_customer()
    product = make_product()
    with pytest.raises(InvalidOrderError):
        order_service.create_order(customer.id, [(product.id, 0)])
