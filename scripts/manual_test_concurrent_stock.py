"""
run python3 -m scripts.manual_test_concurrent_stock
"""

from decimal import Decimal
from unittest.mock import patch

from src.exceptions import InsufficientStockError
from src.patterns.observer.publisher import OrderEventPublisher
from src.repositories.order_repository import OrderRepository
from src.services.customer_service import CustomerService
from src.services.order_service import OrderService
from src.services.product_service import ProductService


def main() -> None:
    product_service = ProductService()
    customer_service = CustomerService()

    product = product_service.add_product(
        name="San pham hiem", category="Test", price=Decimal("100000"), stock_quantity=1
    )
    customer1 = customer_service.add_customer(
        full_name="Nguoi mua A", email="nguoimuaA@example.com", phone="0900000101"
    )
    customer2 = customer_service.add_customer(
        full_name="Nguoi mua B", email="nguoimuaB@example.com", phone="0900000102"
    )

    real_method = OrderRepository.create_order_with_stock_update

    # Gia lap race condition: NGAY TRUOC KHI order_service_2 ghi transaction
    # xuong DB, "chen ngang" cho order_service_1 chay va COMMIT THANH CONG
    # truoc -> luc order_service_2 chay toi UPDATE co dieu kien, thay san
    # pham da het hang that su (khac voi luc no doc/validate luc dau ham)
    order_service_1 = OrderService(order_event_publisher=OrderEventPublisher())
    order_service_2 = OrderService(order_event_publisher=OrderEventPublisher())

    call_count = {"n": 0}

    def racing_create(self, order, stock_deductions):
        call_count["n"] += 1
        if call_count["n"] == 1:
            # Khi order_service_2 goi ham nay lan dau tien -> cho order_service_1
            # chay va commit thanh cong truoc
            order_service_1.create_order(customer1.id, [(product.id, 1)])
        return real_method(self, order, stock_deductions)

    with patch.object(OrderRepository, "create_order_with_stock_update", racing_create):
        order2_result = None
        order2_error = None
        try:
            order2_result = order_service_2.create_order(customer2.id, [(product.id, 1)])
        except InsufficientStockError as e:
            order2_error = e

    # Order cua customer 1 (chen ngang) phai thanh cong
    orders_of_customer1 = order_service_1.search_orders(customer_id=customer1.id)
    assert len(orders_of_customer1) == 1, "Don hang cua customer 1 phai thanh cong"
    print(f"Giao dich chen ngang cua customer 1 thanh cong: {orders_of_customer1[0]}")

    assert order2_result is None
    assert order2_error is not None
    print(f"Giao dich cua customer 2 that bai vi het hang: {order2_error}")

    # Ton kho cuoi cung phai = 0
    final_product = product_service.get_product(product.id)
    assert final_product.stock_quantity == 0, "Ton kho cuoi cung phai = 0"
    print(f"Ton kho cuoi cung cua san pham {final_product.name}: {final_product.stock_quantity}")

    # Khong co order rac cho customer 2
    orders_of_customer2 = order_service_2.search_orders(customer_id=customer2.id)
    assert len(orders_of_customer2) == 0, "Khong co don hang rac cho customer 2"
    print(f"Khong co don hang rac cho customer 2: {orders_of_customer2}")

    print(
        "Test race condition thanh cong: order_service_1 thanh cong, order_service_2 that bai vi het hang."
    )


if __name__ == "__main__":
    main()
