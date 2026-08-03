
from decimal import Decimal, InvalidOperation

def print_error(message: str) -> None:
    print(f"[error] {message}")

def print_success(message: str) -> None:
    print(f"[success] {message}")

def print_info(message: str) -> None:
    print(f"[info] {message}")

def format_money(amount: Decimal) -> str:
    return f"{amount:,.2f} USD"

def prompt_str(prompt: str, allow_empty: bool = False) -> str | None:
    while True:
        raw = input(prompt).strip()
        if not raw:
            if allow_empty:
                return None
            print_error("Input cannot be empty. Please try again.")
            continue
        return raw

def prompt_int(
    prompt: str, allow_empty: bool = False, min_value: int | None = None
) -> int | None:
    while True:
        raw = input(prompt).strip()
        if not raw:
            if allow_empty:
                return None
            print_error("Input cannot be empty. Please try again.")
            continue
        try:
            value = int(raw)
        except ValueError:
            print_error("Invalid integer. Please try again.")
            continue
        if min_value is not None and value < min_value:
            print_error(f"Value must be at least {min_value}. Please try again.")
            continue
        return value

def prompt_decimal(
    prompt: str, allow_empty: bool = False, min_value: Decimal | None = None
) -> Decimal | None:
    while True:
        raw = input(prompt).strip()
        if not raw:
            if allow_empty:
                return None
            print_error("Input cannot be empty. Please try again.")
            continue
        try:
            value = Decimal(raw)
        except InvalidOperation:
            print_error("Invalid decimal number. Please try again.")
            continue
        if min_value is not None and value < min_value:
            print_error(f"Value must be at least {min_value}. Please try again.")
            continue
        return value

def prompt_menu_choice(prompt: str, valid_choices: set[str]) -> str:
    while True:
        raw = input(prompt).strip()
        if raw not in valid_choices:
            print_error(f"Invalid choice. Please choose from {', '.join(valid_choices)}.")
            continue
        return raw
    
def prompt_yes_no(prompt: str) -> bool:
    while True:
        raw = input(f"{prompt} (y/n): ").strip().lower()
        if raw in {"y", "yes"}:
            return True
        if raw in {"n", "no"}:
            return False
        print_error("Invalid input. Please enter 'y' or 'n'.")

def pause() -> None:
    input("Press Enter to continue...")

def paginate(items: list, page_size: int, render_item) -> None:
    if not items:
        print_info("No items to display.")
        return
    
    total_pages = (len(items) + page_size -1) // page_size
    page = 0
    while True:
        start = page * page_size
        end = start + page_size
        print(f"\nPage {page + 1}/{total_pages}")
        for item in items[start:end]:
            render_item(item)

        if total_pages <= 1:
            return
        
        choice = input("Enter 'n' for next page, 'p' for previous page, or 'q' to quit: ").strip().lower()

        if choice == "n" and page < total_pages - 1:
            page += 1
        elif choice == "p" and page > 0:
            page -= 1
        elif choice == "q":
            return