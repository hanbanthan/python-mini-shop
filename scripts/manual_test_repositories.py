"""
python -m scripts.manual_test_repositories
"""

from decimal import Decimal

from src.exceptions import CustomerNotFoundError, InvalidCustomerDataError, ProductNotFoundError
from src.models.customer import Customer
from src.models.enums import CustomerType, OrderStatus
from src.models.order import Order
from src.models.order_item import OrderItem
from src.models.product import Product
from src.repositories.customer_repository import CustomerRepository
from src.repositories.order_repository import OrderRepository
from src.repositories.product_repository import ProductRepository


def test_product_repository():
    print("\n=== ProductRepository ====")
    repo = ProductRepository()

    product = Product(
        id=None, name="Man hinh Dell 27inch", category="Electronics", price=Decimal("4500000")
    )
    product.increase_stock(10)
    product = repo.add(product)
    print("Added product:", product.id, product.name, product.price, product.stock_quantity)

    fetched = repo.get_by_id_or_raise(product.id)
    assert fetched.name == product.name
    print("get_by_id_or_raise passed:", fetched.name)

    fetched.increase_stock(5)
    repo.update(fetched)
    updated = repo.get_by_id_or_raise(product.id)
    assert updated.stock_quantity == 15
    print("update passed:", updated.stock_quantity)

    results = repo.search(keyword="Dell")
    assert any(p.id == product.id for p in results)
    print("search(keyword='Dell') passed, found", len(results), "results")

    repo.deactivate(product.id)
    deactivated = repo.get_by_id_or_raise(product.id)
    assert not deactivated.is_active
    print("deactivate passed, is_active:", deactivated.is_active)

    try:
        repo.get_by_id_or_raise(9999)
        raise AssertionError("Expected ProductNotFoundError for non-existent product")
    except ProductNotFoundError:
        print("get_by_id_or_raise correctly raised ProductNotFoundError for non-existent product")

    return product.id


def test_customer_repository():
    print("\n=== CustomerRepository ====")
    repo = CustomerRepository()

    customer = Customer(
        id=None,
        full_name="Le Van C",
        email="levanc@example.com",
        phone="0987654321",
        customer_type=CustomerType.REGULAR,
    )
    customer = repo.add(customer)
    print("Added customer:", customer.id, customer.full_name, customer.email)

    fetched = repo.get_by_email(customer.email)
    assert fetched is not None and fetched.id == customer.id
    print("get_by_email passed:", fetched.full_name)

    fetched.upgrade_to_vip()
    repo.update(fetched)
    updated = repo.get_by_id_or_raise(customer.id)
    assert updated.is_vip
    print("upgrade_to_vip passed, is_vip:", updated.is_vip)

    try:
        duplicate = Customer(
            id=None,
            full_name="Duplicate Customer",
            email=customer.email,
            phone="0123456789",
            customer_type=CustomerType.REGULAR,
        )
        repo.add(duplicate)
        raise AssertionError("Expected InvalidCustomerDataError for duplicate email")
    except InvalidCustomerDataError:
        print("add correctly raised InvalidCustomerDataError for duplicate email")

    try:
        repo.get_by_id_or_raise(9999)
        raise AssertionError("Expected CustomerNotFoundError for non-existent customer")
    except CustomerNotFoundError:
        print("get_by_id_or_raise correctly raised CustomerNotFoundError for non-existent customer")

    return customer.id


def test_order_repository(product_id: int, customer_id: int) -> None:
    print("\n=== OrderRepository ====")
    repo = OrderRepository()

    order = Order(id=None, customer_id=customer_id)
    order.add_item(
        OrderItem(
            product_id=product_id,
            product_name_snapshot="Man hinh Dell 27inch",
            quantity=2,
            unit_price_snapshot=Decimal("4500000"),
        )
    )
    order.apply_discount(Decimal("500000"))
    order = repo.add(order)
    print("Added order:", order.id, "Total amount:", order.total_amount)

    fetched = repo.get_by_id_or_raise(order.id)
    assert len(fetched.items) == 1
    assert fetched.total_amount == Decimal("8500000")
    print("get_by_id_or_raise passed, total_amount:", fetched.total_amount)

    fetched.mark_completed()
    repo.update(fetched)
    reloaded = repo.get_by_id_or_raise(order.id)
    assert reloaded.status == OrderStatus.COMPLETED
    print("mark_completed passed, status:", reloaded.status)

    results = repo.search(customer_id=customer_id, status=OrderStatus.COMPLETED)
    assert any(o.id == order.id for o in results)
    print("search(customer_id, status) passed, found", len(results), "results")


def main() -> None:
    product_id = test_product_repository()
    customer_id = test_customer_repository()
    test_order_repository(product_id, customer_id)
    print("\nAll repository tests passed successfully.")


if __name__ == "__main__":
    main()
