"""

Chạy: python3 -m scripts.manual_test_report_service

Tạo dữ liệu mẫu với số liệu ĐÃ TÍNH TAY TRƯỚC, sau đó so sánh với kết quả
report để xác nhận khớp chính xác.

Kịch bản dữ liệu:
- product A: "Dien thoai", gia 1,000,000
- product B: "Phu kien", gia 200,000
- customer1: REGULAR, customer2: VIP

- Order1 (customer1, hom nay): 1x A            -> before=1,000,000  discount=0        total=1,000,000
- Order2 (customer2, HOM QUA): 2x B             -> before=400,000    discount=40,000   total=360,000
- Order3 (customer1, hom nay): 1x A + 3x B      -> before=1,600,000  discount=0        total=1,600,000
- Order4 (customer2, hom nay): 1x A             -> tao xong roi CHUYEN THANH 'cancelled'
                                                    truc tiep qua SQL -> KHONG duoc tinh vao report

=> Tinh tay (chi Order1+2+3, loai Order4 da huy):
   total_orders = 3
   total_before_discount = 1,000,000 + 400,000 + 1,600,000 = 3,000,000
   total_discount        = 0 + 40,000 + 0                  = 40,000
   total_revenue         = 1,000,000 + 360,000 + 1,600,000 = 2,960,000
   best_selling: product B so luong = 2+3 = 5 (hang 1), product A = 1+1 = 2 (hang 2)
   revenue_by_category: "Dien thoai" = 1,000,000+1,000,000 = 2,000,000
                        "Phu kien"   = 400,000+600,000     = 1,000,000
   top_customer: customer1 = 1,000,000+1,600,000 = 2,600,000 (hang 1)
"""

from datetime import datetime, timedelta
from decimal import Decimal

from src.database.connection import DatabaseConnection
from src.models.enums import CustomerType
from src.services.customer_service import CustomerService
from src.services.order_service import OrderService
from src.services.product_service import ProductService
from src.services.report_service import ReportService


def main() -> None:
    db = DatabaseConnection()
    product_service = ProductService()
    customer_service = CustomerService()
    order_service = OrderService()
    report_service = ReportService()

    product_a = product_service.add_product(
        name="Dien thoai Model A",
        category="Dien thoai",
        price=Decimal("1000000"),
        stock_quantity=100,
    )

    product_b = product_service.add_product(
        name="Op lung Model B", category="Phu kien", price=Decimal("200000"), stock_quantity=100
    )

    customer1 = customer_service.add_customer(
        full_name="Khach Thuong",
        email="khachthuong.report@example.com",
        phone="0987654321",
        customer_type=CustomerType.REGULAR,
    )

    customer2 = customer_service.add_customer(
        full_name="khach VIP",
        email="khachvip.report@example.com",
        phone="0987654322",
        customer_type=CustomerType.VIP,
    )

    order1 = order_service.create_order(customer1.id, [(product_a.id, 1)])
    order2 = order_service.create_order(customer2.id, [(product_b.id, 2)])
    order3 = order_service.create_order(customer1.id, [(product_a.id, 1), (product_b.id, 3)])
    order4 = order_service.create_order(customer2.id, [(product_a.id, 1)])

    yesterday = (datetime.now() - timedelta(days=1)).isoformat()
    db.execute_write(
        "UPDATE orders SET created_at = ? WHERE id = ?", (yesterday, order2.id), commit=True
    )

    db.execute_write(
        "UPDATE orders SET status = 'cancelled' WHERE id = ?", (order4.id,), commit=True
    )

    def check(label: str, actual, expected) -> None:
        status = "OK" if actual == expected else "FAIL"
        print(f"{label}: {actual} (expected: {expected}) -> {status}")

    check("total_orders (loai tru cancelled)", report_service.total_orders(), 3)

    summary = report_service.revenue_summary()
    check("total_before_discount", summary["total_before_discount"], Decimal("3000000"))
    check("total_discount", summary["total_discount"], Decimal("40000"))
    check("total_revenue", summary["total_revenue"], Decimal("2960000"))

    best_sellers = report_service.best_selling_products(limit=5)
    print("best selling products:", best_sellers)
    assert best_sellers[0]["product_id"] == product_b.id
    assert best_sellers[0]["total_quantity"] == 5
    assert best_sellers[1]["product_id"] == product_a.id
    assert best_sellers[1]["total_quantity"] == 2
    print("best selling products check passed")

    by_category = report_service.revenue_by_category()
    check("revenue_by_category - Dien thoai", by_category["Dien thoai"], Decimal("2000000"))
    check("revenue_by_category - Phu kien", by_category["Phu kien"], Decimal("1000000"))

    by_day = report_service.revenue_by_day()
    print("revenue by day:", by_day)
    assert len(by_day) == 2
    total_from_days = sum(by_day.values())
    check("total revenue from by_day", total_from_days, Decimal("2960000"))

    avg = report_service.average_order_value()
    expected_avg = Decimal("2960000") / Decimal("3").quantize(Decimal("1.00"))
    check("average_order_value", avg, expected_avg)

    top_orders = report_service.top_orders(limit=2)
    assert top_orders[0]["order_id"] == order3.id
    assert top_orders[0]["total_amount"] == Decimal("1600000")
    assert top_orders[1]["order_id"] == order1.id
    print("top orders check passed")

    top_customers = report_service.top_customers(limit=2)
    assert top_customers[0]["customer_id"] == customer1.id
    check(
        "top_customers - customer1 total_spent", top_customers[0]["total_spent"], Decimal("2600000")
    )
    print("top customers check passed")

    yesterday_start = datetime.now() - timedelta(days=1, hours=1)
    yesterday_end = datetime.now() - timedelta(hours=12)
    orders_yesterday_only = report_service.total_orders(
        date_from=yesterday_start, date_to=yesterday_end
    )
    check("total_orders yesterday only", orders_yesterday_only, 1)

    print("Manual test completed.")


if __name__ == "__main__":
    main()
