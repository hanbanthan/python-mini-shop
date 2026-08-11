from src.cli.io_helpers import (
    format_money,
    paginate,
    pause,
    print_error,
    print_info,
    print_success,
    prompt_int,
    prompt_menu_choice,
    prompt_str,
)
from src.exceptions import AppError
from src.models.enums import OrderStatus
from src.models.order import Order
from src.services.customer_service import CustomerService
from src.services.order_service import OrderService
from src.services.product_service import ProductService

_MENU_TEXT = """
=== Order Management ===
1. Create Order
2. List Orders
3. Detail 1 Order
4. Search/Filter Orders
0. Back to Main Menu
"""


def _render_order_summary(order: Order) -> None:
    print(
        f"  #{order.id} | Customer: {order.customer_id} | "
        f"Total: {format_money(order.total_amount)} | "
        f"Status: {order.status.value} | Created At: {order.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
    )


def _print_invoice(order: Order) -> None:
    print("\n=== Invoice ===")
    print(f"Order ID: {order.id}")
    print(f"Customer: {order.customer_id}")
    print(f"Status: {order.status.value}")
    print(f"Created At: {order.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 40)
    print("\nItems:")
    for item in order.items:
        print(
            f"  {item.product_name_snapshot} x{item.quantity} @ "
            f"{format_money(item.unit_price_snapshot)} = {format_money(item.subtotal)}"
        )
    print("-" * 40)
    print(f"\nTotal Before Discount: {format_money(order.total_before_discount)}")
    print(f"Discount: {format_money(order.discount_amount)}")
    print(f"Total Amount: {format_money(order.total_amount)}")
    print("=" * 30)


def _create_order(
    order_service: OrderService,
    product_service: ProductService,
    customer_service: CustomerService,
) -> None:
    print("\n=== Create Order ===")
    customer_id = prompt_int("Enter customer ID: ", min_value=1)
    customer = customer_service.get_customer(customer_id)
    print(f"Customer: {customer.full_name} ({customer.email})")

    items: list[tuple[int, int]] = []
    while True:
        product_id = prompt_int("Enter product ID to add (or 0 to finish): ", min_value=0)
        if product_id == 0:
            break
        try:
            product = product_service.get_product(product_id)
        except AppError as e:
            print_error(str(e))
            continue
        print(
            f"Product: {product.name} | Price: {format_money(product.price)} | Stock: {product.stock_quantity}"
        )
        quantity = prompt_int(f"Enter quantity for {product.name}: ", min_value=1)
        items.append((product_id, quantity))
        print_info(f"Added {quantity} x {product.name} to the order.")

    if not items:
        print_error("No items added to the order. Order creation cancelled.")
        return

    order = order_service.create_order(customer_id, items)
    print_success(f"Order created successfully with ID: {order.id}")
    _print_invoice(order)


def _list_orders(order_service: OrderService) -> None:
    print("\n=== List Orders ===")
    orders = order_service.list_orders()
    paginate(orders, page_size=5, render_item=_render_order_summary)


def _order_detail(order_service: OrderService) -> None:
    print("\n=== Order Detail ===")
    order_id = prompt_int("Enter order ID: ", min_value=1)
    order = order_service.get_order(order_id)
    _print_invoice(order)


def _search_order(order_service: OrderService) -> None:
    print("\n=== Search/Filter Orders ===")
    customer_id = prompt_int("Enter customer ID to filter (or 0 to skip): ", min_value=0)

    status_choice = prompt_str(
        "Enter order status to filter (completed, pending, cancelled) or leave empty to skip: ",
        allow_empty=True,
    )

    status = None
    if status_choice:
        try:
            status = OrderStatus(status_choice.lower())
        except ValueError:
            print_error("Invalid order status. Skipping status filter.")

    results = order_service.search_orders(customer_id=customer_id, status=status)
    print_info(f"Found {len(results)} order(s) matching the criteria:")
    paginate(results, page_size=5, render_item=_render_order_summary)


_ACTIONS_NO_EXTRA = {
    "2": _list_orders,
    "3": _order_detail,
    "4": _search_order,
}


def order_menu_loop(
    order_service: OrderService, product_service: ProductService, customer_service: CustomerService
) -> None:
    while True:
        choice = prompt_menu_choice(_MENU_TEXT, valid_choices={"0", "1", "2", "3", "4"})
        if choice == "0":
            return
        try:
            if choice == "1":
                _create_order(order_service, product_service, customer_service)
            else:
                _ACTIONS_NO_EXTRA[choice](order_service)
        except AppError as exc:
            print_error(f"Error: {exc}")
        pause()
