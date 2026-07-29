from decimal import Decimal

from src.models.customer import Customer
from src.models.enums import CustomerType
from src.models.order import Order
from src.models.order_item import OrderItem
from src.models.product import Product

def main() -> None:
    laptop = Product(
        id=1,
        name="Laptop Dell XPX 13",
        category="Electronics",
        price=Decimal("2500000"),
        tags={"laptop", "dell", "hot"},
    )
    laptop.increase_stock(10)
    print(f"Product: {laptop.name}, stock={laptop.stock_quantity}, active={laptop.is_active}")

    customer = Customer(
        id=1,
        full_name="Nguyen Van A",
        email="vana@example.com",
        phone="0901234567",
        customer_type=CustomerType.VIP,
    )
    print(f"Customer: {customer.full_name}, is_vip={customer.is_vip}")

    order = Order(id=1, customer_id=customer.id)
    order.add_item(
        OrderItem(
            product_id=laptop.id,
            product_name_snapshot=laptop.name,
            quantity=2,
            unit_price_snapshot=laptop.price,
        )
    )
    print(f"Order total before discount: {order.total_before_discount}")

    order.apply_discount(Decimal("200000"))
    print(f"Order discount: {order.discount_amount}, total: {order.total_amount}")

    laptop.reduce_stock(2)
    print(f"Product stock after sale: {laptop.stock_quantity}")

    order.mark_completed()
    print(f"Order status: {order.status}")

    print("Checkpoint 1: OK")

if __name__ == "__main__":
    main()