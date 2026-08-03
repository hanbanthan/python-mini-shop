from src.cli.io_helpers import (
    pause,
    paginate,
    print_error,
    print_info,
    print_success,
    prompt_int,
    prompt_menu_choice,
    prompt_str,
    prompt_yes_no,
)
from src.exceptions import AppError
from src.models.customer import Customer
from src.models.enums import CustomerType
from src.services.customer_service import CustomerService

_MENU_TEXT = """
=== Customer Management ===
1. Add Customer
2. List Customers
3. Search Customer
4. Update Customer
5. Upgrade/Downgrade Customer Type
6. Delete Customer
0. Back to Main Menu
"""

def _render_customer(c: Customer) -> None:
    print(
        f"  #{c.id} | {c.full_name} | {c.email} | {c.phone} | "
        f"{c.customer_type.value}"
    )

def _add_customer(service: CustomerService) -> None:
    print("\n=== Add Customer ===")
    full_name = prompt_str("Enter full name: ")
    email = prompt_str("Enter email: ")
    phone = prompt_str("Enter phone number: ")
    is_vip = prompt_yes_no("Is this customer a VIP?")
    customer_type = CustomerType.VIP if is_vip else CustomerType.REGULAR

    customer = service.add_customer(
        full_name=full_name, email=email, phone=phone, customer_type=customer_type
    )
    print_success(f"Customer added successfully with ID: {customer.id} {customer.full_name}")

def _list_customers(service: CustomerService) -> None:
    print("\n=== List Customers ===")
    customers = service.list_customers()
    paginate(customers, page_size=5, render_item=_render_customer)

def _search_customer(service: CustomerService) -> None:
    print("\n=== Search Customer ===")
    keyword = prompt_str("Enter name or email to search: ", allow_empty=True)
    results = service.search_customers(keyword=keyword)
    print_info(f"Found {len(results)} customer(s) matching '{keyword}':")
    paginate(results, page_size=5, render_item=_render_customer)

def _update_customer(service: CustomerService) -> None:
    print("\n=== Update Customer ===")
    customer_id = prompt_int("Enter customer ID to update: ", min_value=1)
    current = service.get_customer(customer_id)
    print_info(f"Current details: {current.full_name} | {current.email} | {current.phone} | {current.customer_type.value}")
    _render_customer(current)   

    print("Enter new details (leave blank to keep current value):")
    full_name = prompt_str("New full name: ", allow_empty=True)
    email = prompt_str("New email: ", allow_empty=True)
    phone = prompt_str("New phone number: ", allow_empty=True)

    updated = service.update_customer(
        customer_id=customer_id,
        full_name=full_name,
        email=email,
        phone=phone
    )
    print_success(f"Customer updated successfully: #{updated.id} {updated.full_name}")
    _render_customer(updated)

def _change_customer_tier(service: CustomerService) -> None:
    print("\n=== Upgrade/Downgrade Customer Type ===")
    customer_id = prompt_int("Enter customer ID: ", min_value=1)
    current = service.get_customer(customer_id)
    _render_customer(current)

    if current.customer_type == CustomerType.VIP:
        if prompt_yes_no("Downgrade to Regular?"):
            updated = service.downgrade_to_regular(customer_id)
            print_success(f"Customer downgraded to Regular: #{updated.id} {updated.full_name}")
    else:
        if prompt_yes_no("Upgrade to VIP?"):
            updated = service.upgrade_to_vip(customer_id)
            print_success(f"Customer upgraded to VIP: #{updated.id} {updated.full_name}")
        
def _remove_customer(service: CustomerService) -> None:
    print("\n=== Delete Customer ===")
    customer_id = prompt_int("Enter customer ID to delete: ", min_value=1)
    service.get_customer(customer_id)  
    if not prompt_yes_no(f"Are you sure you want to delete customer ID {customer_id}?"):
        print_info("Operation cancelled.")
        return
    service.remove_customer(customer_id)
    print_success(f"Customer ID {customer_id} has been deleted.")

_ACTIONS = {
    "1": _add_customer,
    "2": _list_customers,
    "3": _search_customer,
    "4": _update_customer,
    "5": _change_customer_tier,
    "6": _remove_customer,
}

def customer_menu_loop(service: CustomerService) -> None:
    while True:
        choice = prompt_menu_choice(_MENU_TEXT, valid_choices=set(_ACTIONS) | {"0"})
        if choice == "0":
            return
        try:
            _ACTIONS[choice](service)
        except AppError as exc:
            print_error(f"Error: {exc}")
        pause()
