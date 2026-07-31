"""
python -m scripts.manual_test_services
"""

from decimal import Decimal

from src.services.customer_service import CustomerService
from src.services.product_service import ProductService
from src.services.order_service import OrderService
from src.exceptions import InvalidProductDataError, ProductNotFoundError, CustomerNotFoundError, InvalidCustomerDataError, InsufficientStockError, InvalidOrderError, CustomerNotFoundError
from src.models.enums import CustomerType, OrderStatus
from src.database.connection import DatabaseConnection

def test_order_service():
    print("\n=== OrderService ====")
    db = DatabaseConnection()
    product_service = ProductService()
    customer_service = CustomerService()
    order_service = OrderService()

    laptop= product_service.add_product(
        name="Laptop Dell XPS 13",
        category="Electronics",
        price=Decimal("30000000"),
        stock_quantity=5,
    )

    mouse = product_service.add_product(
        name="Mouse Logitech MX Master 3",
        category="Electronics",
        price=Decimal("2000000"),
        stock_quantity=10,
    )

    vip_customer = customer_service.add_customer(
        full_name="VIP Customer",
        email="vip@example.com",
        phone="0987654321",
        customer_type=CustomerType.VIP
    )

    # 1. Create order
    order = order_service.create_order(
        customer_id=vip_customer.id,
        items=[(laptop.id, 1), (mouse.id, 2)]
    )
    print("Created order:", order.id)

    expected_before_discount = laptop.price * 1 + mouse.price * 2
    assert order.total_before_discount == expected_before_discount
    
    expected_discount = expected_before_discount * Decimal("15")/Decimal("100").quantize(Decimal("0.01"))
    assert order.discount_amount == expected_discount
    assert order.total_amount == expected_before_discount - expected_discount
    print("Before discount:", order.total_before_discount, "Discount:", order.discount_amount, "Total:", order.total_amount)

    # Check DB for order and order items and stock quantity
    order_row = db.fetch_one("SELECT * FROM orders WHERE id = ?", (order.id,))
    assert order_row is not None
    assert order_row["status"] == OrderStatus.COMPLETED.value
    print("Closed order status:", order_row["status"])

    item_rows = db.fetch_all("SELECT * FROM order_items WHERE order_id = ?", (order.id,))
    assert len(item_rows) == 2
    print("Order items count:", len(item_rows))

    laptop_row = db.fetch_all("SELECT stock_quantity FROM products WHERE id = ?", (laptop.id,))
    mouse_row = db.fetch_all("SELECT stock_quantity FROM products WHERE id = ?", (mouse.id,))
    assert laptop_row[0]["stock_quantity"] == 4
    assert mouse_row[0]["stock_quantity"] == 8
    print("Stock quantity after order: Laptop:", laptop_row[0]["stock_quantity"])

    # 2. Test get_order
    fetched_order = order_service.get_order(order.id)
    assert len(fetched_order.items) == 2
    print("get_order passed, items count:", len(fetched_order.items))

    # 3. Test search_orders
    results = order_service.search_orders(customer_id=vip_customer.id, status=OrderStatus.COMPLETED)
    assert any(o.id == order.id for o in results)
    print("search_orders passed, found", len(results), "results")

    # 4. Test empty order
    try:
        order_service.create_order(customer_id=vip_customer.id, items=[])
        raise AssertionError("Expected InvalidOrderError for empty order")
    except InvalidOrderError:
        print("create_order correctly raised InvalidOrderError for empty order")
    
    # 5. Test not existing customer
    try:
        order_service.create_order(customer_id=9999, items=[(laptop.id, 1)])
        raise AssertionError("Expected CustomerNotFoundError for non-existent customer")
    except CustomerNotFoundError:
        print("create_order correctly raised CustomerNotFoundError for non-existent customer")  
    
    # 6. buy over stock_quantity -> rollback, no rubbish
    orders_before = db.fetch_one("SELECT COUNT(*) AS c from orders")["c"]
    order_items_before = db.fetch_one("SELECT COUNT(*) AS c from order_items")["c"]
    laptop_stock_before = db.fetch_one("SELECT stock_quantity FROM products WHERE id = ?", (laptop.id,))["stock_quantity"]

    try:
        order_service.create_order(customer_id=vip_customer.id, items=[(laptop.id, 100)])
        raise AssertionError("Expected InsufficientStockError for buying over stock quantity")
    except InsufficientStockError:
        print("create_order correctly raised InsufficientStockError for buying over stock quantity")

    orders_after = db.fetch_one("SELECT COUNT(*) AS c from orders")["c"]
    order_items_after = db.fetch_one("SELECT COUNT(*) AS c from order_items")["c"]
    laptop_stock_after = db.fetch_one("SELECT stock_quantity FROM products WHERE id = ?", (laptop.id,))["stock_quantity"]

    assert orders_before == orders_after
    assert order_items_before == order_items_after
    assert laptop_stock_before == laptop_stock_after

    print("Orders count before:", orders_before, "after:", orders_after)
    print("Order items count before:", order_items_before, "after:", order_items_after)
    print("Laptop stock before:", laptop_stock_before, "after:", laptop_stock_after)    


def test_product_service():
    print("\n=== ProductService ====")
    service = ProductService()

    # 1. Add a correct product
    product = service.add_product(
        name="Test Product",
        category="Test Category",
        price=Decimal("1500000"),
        stock_quantity=10,
        tags={"test", "product"}
    )
    print("Added product:", product.id, product.name, product.price, product.stock_quantity)

    # 2. Add a incorrect product
    try:
        service.add_product(
            name="",
            category="Test Category",
            price=Decimal("100"),
            stock_quantity=1,
        )
        raise AssertionError("it should raise InvalidProductDataError (empty name)")
    except InvalidProductDataError:
        print("Correctly raised InvalidProductDataError for empty name")
    
    try:
        service.add_product(
            name="Test",
            category="Test Category",
            price=Decimal("-100"),
            stock_quantity=1,
        )
        raise AssertionError("it should raise InvalidProductDataError (negative price)")
    except InvalidProductDataError:
        print("Correctly raised InvalidProductDataError for negative price")
    
    try:
        service.add_product(
            name="Test",
            category="Test Category",
            price=Decimal("100"),
            stock_quantity=-5,
        )
        raise AssertionError("It should raise InvalidProductDataError (negative stock qunantity)")
    except InvalidProductDataError:
        print("Correctly raised InvalidProductDataError for negative stock quantity")
    
    # 3. Find product existing
    found = service.get_product(product.id)
    assert found.name == product.name
    print("get_product_by_id passed:", found.name)

    # 4. Find product not existing
    try:
        service.get_product(9999)
        raise AssertionError("Expected ProductNotFoundError for non-existent product")  
    except ProductNotFoundError:
        print("get_product_by_id correctly raised ProductNotFoundError for non-existent product")   
    
    # 5. Search according to keyword + tag + price range
    results = service.search_products(keyword="Test", tag="product", min_price=Decimal("1000000"))
    assert any(p.id == product.id for p in results)
    print("search_products passed, found", len(results), "results")

    results_out_of_range = service.search_products(keyword="Test", tag="product", min_price=Decimal("2000000"))
    assert not any(p.id == product.id for p in results_out_of_range)
    print("search_products with min_price out of range passed, found", len(results_out_of_range), "results")

    # 6. Update product
    updated = service.update_product(product.id, price=Decimal("1400000"))
    assert updated.price == Decimal("1400000")
    assert updated.name == product.name
    print("update_product passed new price, name unchanged :", updated.price, updated.name)

    # 7. Update product with correct stock quantity
    updated = service.update_product(product.id, stock_quantity=20)
    assert updated.stock_quantity == 20
    print("update_product passed new stock quantity:", updated.stock_quantity)

    # 8. Update product with incorrect stock quantity
    try:
        service.update_product(product.id, stock_quantity=-5)
        raise AssertionError("Expected InvalidProductDataError for negative stock quantity")
    except InvalidProductDataError:
        print("update_product correctly raised InvalidProductDataError for negative stock quantity")
    
    # 9. Update product not existing
    try:
        service.update_product(9999, price=Decimal("100"))
        raise AsssertionError("Expected ProductNotFoundError for non-existent product")
    except ProductNotFoundError:
        print("update_product correctly raised ProductNotFoundError for non-existent product")

    # 10. Delete never sold product -> hard delete
    never_sold = service.add_product(
        name="Never Sold Product",
        category="Test Category",
        price=Decimal("1000000"),
        stock_quantity=5,
    )
    service.remove_product(never_sold.id)
    try:
        service.get_product(never_sold.id)
        raise AssertionError("Expected ProductNotFoundError for deleted product")
    except ProductNotFoundError:
        print("remove_product correctly hard deleted never sold product")
    
def test_customer_service():
    print("\n=== CustomerService ====")
    service = CustomerService()

    # 1. Add a correct customer
    customer = service.add_customer(
        full_name="Test Customer",
        email="test@example.com",
        phone="1234567890"
    )
    print("Added customer:", customer.id, customer.full_name, customer.email)

    # 2. Add a customer with incorrect email
    try:
        service.add_customer(
            full_name="Test Customer 2",
            email="not an email",
            phone="0987654321"
        )
        raise AssertionError("Expected InvalidCustomerDataError for invalid email")
    except InvalidCustomerDataError:
        print("Correctly raised InvalidCustomerDataError for invalid email")

    # 3. Add a customer with existing email
    try:
        service.add_customer(
            full_name="Test Customer 3",
            email="test@example.com",
            phone="0987654321"
        )
        raise AssertionError("Expected InvalidCustomerDataError for existing email")
    except InvalidCustomerDataError:
        print("Correctly raised InvalidCustomerDataError for existing email")

    # 4. Get existing customer
    found = service.get_customer(customer.id)
    assert found.email == customer.email
    print("get_customer passed:", found.full_name)

    # 5. Get non-existing customer
    try:
        service.get_customer(9999)
        raise AssertionError("Expected CustomerNotFoundError for non-existent customer")
    except CustomerNotFoundError:
        print("get_customer correctly raised CustomerNotFoundError for non-existent customer")

    # 6. Search customers by name or email
    results = service.search_customers(keyword="Test")
    assert any(c.id == customer.id for c in results)
    print("search_customers passed, found", len(results), "results")

    # 7. Update customer
    updated = service.update_customer(customer.id, phone="0987654321")
    assert updated.phone == "0987654321"
    assert updated.full_name == customer.full_name
    print("update_customer passed new phone, name unchanged:", updated.phone, updated.full_name)

    # 8. Update customer with incorrect email
    try:
        service.update_customer(customer.id, email="incorrect email")
        raise AssertionError("Expected InvalidCustomerDataError for invalid email")
    except InvalidCustomerDataError:
        print("update_customer correctly raised InvalidCustomerDataError for invalid email")
    
    # 9. Update with not existing customer
    try:
        service.update_customer(9999, phone="0123456789")
        raise AssertionError("Expected CustomerNotFoundError for non-existent customer")
    except CustomerNotFoundError:
        print("update_customer correctly raised CustomerNotFoundError for non-existent customer")

    # 10. Upgrade customer to VIP
    vip_customer = service.upgrade_to_vip(customer.id)
    assert vip_customer.customer_type == CustomerType.VIP
    print("upgrade_to_vip passed, customer_type:", vip_customer.customer_type)

    # 11. Downgrade customer to REGULAR
    regular_customer = service.downgrade_to_regular(customer.id)
    assert regular_customer.customer_type == CustomerType.REGULAR
    print("downgrade_to_regular passed, customer_type:", regular_customer.customer_type)

    # 12. Delete customer with no orders 
    no_order_customer = service.add_customer(
        full_name="No Order Customer",
        email="noorder@example.com",
        phone="1112223333"
    )
    service.remove_customer(no_order_customer.id)
    try:
        service.get_customer(no_order_customer.id)
        raise AssertionError("Expected CustomerNotFoundError for deleted customer")
    except CustomerNotFoundError:
        print("remove_customer correctly hard deleted customer with no orders")

def main() -> None:
    product_id = test_product_service()
    customer_id = test_customer_service()
    order_id = test_order_service()
    print("All service tests passed successfully.")

if __name__ == "__main__":
    main()