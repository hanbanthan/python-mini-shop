from src.cli.customer_menu import customer_menu_loop
from src.cli.io_helpers import print_error, prompt_menu_choice
from src.cli.order_menu import order_menu_loop
from src.cli.product_menu import product_menu_loop
from src.cli.report_menu import report_menu_loop
from src.exceptions import AppError
from src.services.customer_service import CustomerService
from src.services.order_service import OrderService
from src.services.product_service import ProductService
from src.services.report_service import ReportService

_MAIN_MENU_TEXT = """
=== Mini Shop Management System ===
1. Product Management
2. Customer Management
3. Order Management
4. Report Management
0. Exit
"""


def run() -> None:
    product_service = ProductService()
    customer_service = CustomerService()
    order_service = OrderService()
    report_service = ReportService()

    print("Welcome to the Mini Shop Management System!")

    while True:
        try:
            choice = prompt_menu_choice(_MAIN_MENU_TEXT, valid_choices={"0", "1", "2", "3", "4"})
        except (EOFError, KeyboardInterrupt):
            print("\nExiting the application. Goodbye!")
            return

        if choice == "0":
            print("Exiting the application. Goodbye!")
            return

        try:
            if choice == "1":
                product_menu_loop(product_service)
            elif choice == "2":
                customer_menu_loop(customer_service)
            elif choice == "3":
                order_menu_loop(order_service, product_service, customer_service)
            elif choice == "4":
                report_menu_loop(report_service)
        except AppError as exc:
            print_error(f"Error: {exc}")
        except (EOFError, KeyboardInterrupt):
            print("\nReturning to main menu.")
            return
