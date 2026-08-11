"""

The flow of create order:
Check if customer exists -> Check if each product exists and active
-> Check if each product has enough stock
-> block empty order
-> calculate total price (snapshot name, price)
-> apply discount (stategy pattern)
-> write order + order iotems + update stock quantity in
1 ONLY transaction (atomic, rollback if enything fails
in OrderRepository.create_order_with_stock_updates())

"""

from datetime import datetime

from src.exceptions import InsufficientStockError, InvalidOrderError
from src.models.enums import OrderStatus
from src.models.order import Order
from src.models.order_item import OrderItem
from src.patterns.discount.factory import DiscountPolicyFactory
from src.patterns.observer.base import OrderCreatedEvent
from src.patterns.observer.default_publisher import build_default_order_event_publisher
from src.patterns.observer.publisher import OrderEventPublisher
from src.repositories.customer_repository import CustomerRepository
from src.repositories.order_repository import OrderRepository
from src.repositories.product_repository import ProductRepository


class OrderService:
    def __init__(
        self,
        order_repository: OrderRepository | None = None,
        product_repository: ProductRepository | None = None,
        customer_repository: CustomerRepository | None = None,
        order_event_publisher: OrderEventPublisher | None = None,
    ) -> None:
        self._order_repo = order_repository or OrderRepository()
        self._product_repo = product_repository or ProductRepository()
        self._customer_repo = customer_repository or CustomerRepository()
        self._publisher = order_event_publisher or build_default_order_event_publisher()

    def create_order(self, customer_id: int, items: list[tuple[int, int]]) -> Order:
        if not items:
            raise InvalidOrderError("Order must contain at least one item")

        customer = self._customer_repo.get_by_id_or_raise(customer_id)

        merged_quantities: dict[int, int] = {}
        for product_id, quantity in items:
            if quantity <= 0:
                raise InvalidOrderError(f"Quantity for product {product_id} must be positive")
            merged_quantities[product_id] = merged_quantities.get(product_id, 0) + quantity

        products_by_id = {}
        for product_id, quantity in merged_quantities.items():
            product = self._product_repo.get_by_id_or_raise(product_id)
            if not product.is_active:
                raise InvalidOrderError(f"Product {product.name} is not active")
            if quantity > product.stock_quantity:
                raise InsufficientStockError(
                    f"Not enough stock for product {product.name}"
                    f" (requested {quantity}, available {product.stock_quantity})"
                )
            products_by_id[product_id] = product

        order = Order(id=None, customer_id=customer_id)
        for product_id, quantity in merged_quantities.items():
            product = products_by_id[product_id]
            order.add_item(
                OrderItem(
                    product_id=product_id,
                    product_name_snapshot=product.name,
                    quantity=quantity,
                    unit_price_snapshot=product.price,
                )
            )
        order.validate_not_empty()

        discount_policy = DiscountPolicyFactory.get_policy(customer.customer_type)
        discount_amount = discount_policy.calculate_discount(order.total_before_discount)
        order.apply_discount(discount_amount)

        stock_deductions: dict[int, int] = {}
        for product_id, quantity in merged_quantities.items():
            stock_deductions[product_id] = quantity

        order.mark_completed()
        created_order = self._order_repo.create_order_with_stock_update(order, stock_deductions)

        self._publisher.notify(OrderCreatedEvent(order=created_order, customer=customer))

        return created_order

    def list_orders(self) -> list[Order]:
        return self._order_repo.get_all()

    def get_order(self, order_id: int) -> Order:
        return self._order_repo.get_by_id_or_raise(order_id)

    def search_orders(
        self,
        customer_id: int | None = None,
        status: OrderStatus | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> list[Order]:
        return self._order_repo.search(
            customer_id=customer_id, status=status, date_from=date_from, date_to=date_to
        )

    def cancel_order(self, order_id: int) -> Order:
        order = self._order_repo.get_by_id_or_raise(order_id)

        if order.status != OrderStatus.COMPLETED:
            raise InvalidOrderError("Only completed orders can be canceled")

        stock_deductions: dict[int, int] = {}

        for item in order.items:
            product = self._product_repo.get_by_id_or_raise(item.product_id)
            product.increase_stock(item.quantity)
            stock_deductions[item.product_id] = product.stock_quantity

        order.cancel()

        self._order_repo.cancel_order_with_stock_update(
            order,
            stock_deductions,
        )

        return order
