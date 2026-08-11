"""
python -m scripts.manual_test_observer

Check
1. create order successfully -> only see log/notification from
3 obsevers(stock update, audit log, notification) independently

2. audit log write in seperate file

3. OrderService not hard code depend on any specific observer:
can subscribe 1 more observer, no need to change OrderService

4. 1 observer fail -> not affect other observers, not
affect flow of main order

"""

from decimal import Decimal
from pathlib import Path
from uuid import uuid4

from src.config.logging_config import LOG_DIR, configure_logging
from src.models.enums import CustomerType
from src.patterns.observer.base import OrderCreatedEvent, OrderObserver
from src.patterns.observer.publisher import OrderEventPublisher
from src.services.customer_service import CustomerService
from src.services.order_service import OrderService
from src.services.product_service import ProductService


class FakeSpyObserver(OrderObserver):
    def __init__(self) -> None:
        self.called_with: OrderCreatedEvent | None = None

    def on_order_created(self, event: OrderCreatedEvent) -> None:
        self.called_with = event
        print(f"FakeSpyObserver called with event: {event}")


class BuggyObserver(OrderObserver):
    def on_order_created(self, event: OrderCreatedEvent) -> None:
        raise RuntimeError("Intentional error in buggyObserver")


def main() -> None:
    configure_logging()

    run_id = uuid4().hex

    product_service = ProductService()
    customer_service = CustomerService()

    product = product_service.add_product(
        name=f"Test Product {run_id}",
        category=f"Test Category {run_id}",
        price=Decimal("10.00"),
        stock_quantity=100,
    )

    customer = customer_service.add_customer(
        full_name="Test Customer",
        email=f"test.customer.{run_id}@example.com",
        phone="1234567890",
        customer_type=CustomerType.REGULAR,
    )

    # 1 Use default publisher  -> observe log/print
    print("\n=== Test 1: Default Publisher ====")
    order_service_default = OrderService()
    order = order_service_default.create_order(customer_id=customer.id, items=[(product.id, 1)])
    print(f"Order created with ID: {order.id}, Total: {order.total_amount}")

    # 2. Check audit.log write to seperate file

    audit_log_path = Path(LOG_DIR) / "audit.log"
    assert audit_log_path.exists(), "audit.log file must exist"
    content = audit_log_path.read_text()

    print("LOG CONTENT:")
    print(content)

    assert f"order_id={order.id}" in content
    print("Audit log written to audit.log successfully.")

    # 3. OrderService not hard code depend on any specific observer -> subscibe 1 more observer
    print("\n=== Test 3: Custom Publisher with FakeSpyObserver ====")
    custome_publisher = OrderEventPublisher()
    spy = FakeSpyObserver()
    custome_publisher.subscribe(spy)

    order_service_custome = OrderService(order_event_publisher=custome_publisher)
    order2 = order_service_custome.create_order(customer_id=customer.id, items=[(product.id, 2)])

    assert spy.called_with is not None
    assert spy.called_with.order.id == order2.id
    print(f"FakeSpyObserver called with event for order ID: {spy.called_with.order.id}")

    # 4. 1 observer fail -> not affect other observers, not affect flow of main order
    print("\n=== Test 4: Buggy Observer ====")
    mixed_publisher = OrderEventPublisher()
    spy2 = FakeSpyObserver()
    mixed_publisher.subscribe(BuggyObserver())
    mixed_publisher.subscribe(spy2)

    order_service_mixed = OrderService(order_event_publisher=mixed_publisher)
    order3 = order_service_mixed.create_order(customer_id=customer.id, items=[(product.id, 3)])

    assert order3 is not None
    assert spy2.called_with is not None
    assert spy2.called_with.order.id == order3.id
    print(f"Order created with ID: {order3.id}, Total: {order3.total_amount}")

    print("\nAll tests passed successfully.")


if __name__ == "__main__":
    main()
