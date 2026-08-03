from datetime import datetime

from src.cli.io_helpers import format_money, pause, print_error, print_info, prompt_menu_choice, prompt_str
from src.exceptions import AppError
from src.services.report_service import ReportService

_MENU_TEXT = """
=== Report Management ===
1. Report all time
2. Report by date range
0. Back to Main Menu
"""

def _print_report(report: dict) -> None:
    print("\n=== Report ===")
    print(f"Total orders: {report['total_orders']}")
    summary = report["revenue_summary"]
    print(f"Total before discount: {format_money(summary['total_before_discount'])}")
    print(f"Total discount: {format_money(summary['total_discount'])}")
    print(f"Total revenue: {format_money(summary['total_revenue'])}")
    print(f"Average order value: {format_money(summary['average_order_value'])}")

    print("\n Best-selling products:")
    if not report["best_selling_products"]:
        print("  No products sold in this period.")
    for item in report["best_selling_products"]:
        print(f"  {item['product_name']} - Quantity sold: {item['total_quantity']}")
    
    print("\n Revenue by category:")
    if not report["revenue_by_category"]:
        print("  No revenue in this period.")
    for item in report["revenue_by_category"]:
        print(f"  {item['category']} - Revenue: {format_money(item['total_revenue'])}")

    print("\n Revenue by day:")
    if not report["revenue_by_day"]:
        print("  No revenue in this period.")
    for item in report["revenue_by_day"]:
        print(f"  {item['date']} - Revenue: {format_money(item['total_revenue'])}")
    
    print("\n Top orders by revenue:")
    if not report["top_orders"]:
        print("  No orders in this period.")
    for order_info in report["top_orders"]:
        print(f"  Order ID: {order_info['order_id']} - Total Amount: {format_money(order_info['total_amount'])}")

    print("\n Top customers by spending:")
    if not report["top_customers"]:
        print("  No customers in this period.")
    for customer_info in report["top_customers"]:
        print(f"  {customer_info['customer_name']} - Total Spending: {format_money(customer_info['total_spending'])}")

def _full_report(service: ReportService) -> None:
    report = service.full_report()
    _print_report(report)

def _custom_range_report(service: ReportService) -> None:
    print("\n=== Report by Date Range ===")
    print("\n format: YYYY-MM-DD. Empty means no limit.")
    date_from_str = prompt_str("Enter start date: ", allow_empty=True)
    date_to_str = prompt_str("Enter end date: ", allow_empty=True)
    report = service.date_range_report(date_from_str, date_to_str)
    _print_report(report)

def _prompt_optional_date(prompt_text: str):
    while True:
        raw = prompt_str(prompt_text, allow_empty=True)
        if not raw:
            return None
        try:
            return datetime.strptime(raw, "%Y-%m-%d")
        except ValueError:
            print_error("Invalid date format. Please use YYYY-MM-DD.")

_ACTIONS = {
    "1": _full_report,
    "2": _custom_range_report,
}

def report_menu_loop(service: ReportService) -> None:
    while True:
        print(_MENU_TEXT)
        choice = prompt_menu_choice("Select an option: ", valid_choices=set(_ACTIONS.keys()).union({"0"}))
        if choice == "0":
            break
        action = _ACTIONS.get(choice)
        if action:
            action(service)
            pause()