from decimal import Decimal

from src.cli.io_helpers import (
    format_money,
    paginate,
    pause,
    print_error,
    print_info,
    print_success,
    prompt_decimal,
    prompt_int,
    prompt_menu_choice,
    prompt_str,
    prompt_yes_no,
)
from src.exceptions import AppError
from src.models.product import Product
from src.services.product_service import ProductService

_MENU_TEXT = """
=== Product Management ===
1. Add Product
2. List Products
3. Search Product
4. Update Product
5. Delete/Deactivate Product
0. Back to Main Menu
"""


def _render_product(p: Product) -> None:
    status = "Active" if p.is_active else "Inactive"
    tags = ", ".join(p.tags) if p.tags else "None"
    print(
        f"  #{p.id} | {p.name} | {p.category} | {format_money(p.price)} | "
        f"Ton kho: {p.stock_quantity} | {status} | Tags: {tags}"
    )


def _add_product(service: ProductService) -> None:
    print("\n=== Add Product ===")
    name = prompt_str("Enter product name: ")
    category = prompt_str("Enter product category: ")
    price = prompt_decimal("Enter product price: ", min_value=Decimal("0.01"))
    stock = prompt_int("Enter stock quantity: ", min_value=0)
    tags_raw = prompt_str("Enter tags (comma-separated, optional): ", allow_empty=True)
    tags = {tag.strip() for tag in tags_raw.split(",")} if tags_raw else set()

    product = service.add_product(
        name=name, category=category, price=price, stock_quantity=stock, tags=tags
    )
    print_success(f"Product added successfully with ID: {product.id} {product.name}")


def _list_products(service: ProductService) -> None:
    """(Nang cao) Dung phan tran LIMIT/OFFSET that o DB - moi lan sang
    trang la 1 query moi, chi doc dung so dong can thiet (khac voi
    `_search_product` ben duoi van dung 'paginate()' phia client vi ket
    qua search da duoc loc, so luong nho, khong can toi uu DB -level)
    """
    print("\n=== List Products ===")
    page = 1
    page_size = 5
    while True:
        products, total_pages = service.list_products_page(page=page, page_size=page_size)
        print(
            f"\n--- Page {page}/{total_pages} (LIMIT {page_size} OFFSET {(page - 1) * page_size}) ---"
        )
        if not products:
            print_info("No products found.")
        for p in products:
            _render_product(p)

        if total_pages <= 1:
            return
        choice = (
            input(
                f"\nEnter 'n' for next page, 'p' for previous page, or 'q' to quit (current page {page}/{total_pages}): "
            )
            .strip()
            .lower()
        )
        if choice == "n" and page < total_pages:
            page += 1
        elif choice == "p" and page > 1:
            page -= 1
        elif choice == "q":
            return


def _search_product(service: ProductService) -> None:
    print("\n=== Search Product ===")
    keyword = prompt_str("Enter product name or category to search: ")
    category = prompt_str("Enter category to filter (optional): ", allow_empty=True)
    min_price = prompt_decimal("Enter minimum price (optional): ", allow_empty=True)
    max_price = prompt_decimal("Enter maximum price (optional): ", allow_empty=True)
    tag = prompt_str("Enter tag to filter (optional): ", allow_empty=True)
    active_only = prompt_yes_no("Show only active products?")

    results = service.search_products(
        keyword=keyword,
        category=category,
        min_price=min_price,
        max_price=max_price,
        tag=tag,
        active_only=active_only,
    )
    print(f"\nFound {len(results)} product(s) matching the criteria.")
    paginate(results, page_size=5, render_item=_render_product)


def _update_product(service: ProductService) -> None:
    print("\n=== Update Product ===")
    product_id = prompt_int("Enter product ID to update: ", min_value=1)
    current = service.get_product(product_id)
    print("Current product details:")
    _render_product(current)

    print("\nEnter new values (leave blank to keep current value):")
    name = prompt_str("New name: ", allow_empty=True)
    category = prompt_str("New category: ", allow_empty=True)
    price = prompt_decimal("New price: ", allow_empty=True, min_value=Decimal("0.01"))
    stock = prompt_int("New stock quantity: ", allow_empty=True, min_value=0)

    updated = service.update_product(
        product_id=product_id, name=name, category=category, price=price, stock_quantity=stock
    )
    print_success(f"Product updated successfully: #{updated.id} {updated.name}")
    _render_product(updated)


def _remove_product(service: ProductService) -> None:
    print("\n=== Delete/Deactivate Product ===")
    product_id = prompt_int("Enter product ID to delete/deactivate: ", min_value=1)
    service.get_product(product_id)
    if not prompt_yes_no(f"Are you sure you want to delete/deactivate product ID {product_id}?"):
        print_info("Operation cancelled.")
        return
    service.remove_product(product_id)
    print_success(f"Product ID {product_id} has been deleted/deactivated.")


_ACTIONS = {
    "1": _add_product,
    "2": _list_products,
    "3": _search_product,
    "4": _update_product,
    "5": _remove_product,
}


def product_menu_loop(service: ProductService) -> None:
    while True:
        choice = prompt_menu_choice(_MENU_TEXT, valid_choices=set(_ACTIONS) | {"0"})
        if choice == "0":
            return
        try:
            _ACTIONS[choice](service)
        except AppError as exc:
            print_error(f"Error: {exc}")
        pause()
