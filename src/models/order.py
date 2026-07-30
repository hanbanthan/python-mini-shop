"""Model Order

Use dataclass for the data (id, customer_id, timestamps,...)
but do not let items/discount to be public fields, using property + method
to encapsulate the logic of adding/removing items and applying discount

- total_before_discount: calculated from substotal of items
- discount_amount: assigned from apply_discount method
- total amount = total_before_discount - discount_amount
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal

from src.exceptions import InvalidOrderError
from src.models.enums import OrderStatus
from src.models.order_item import OrderItem

@dataclass
class Order:
    id: int | None
    customer_id: int
    status: OrderStatus = OrderStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    # private fields 
    _items: list[OrderItem] = field(default_factory=list, repr=False)
    _discount_amount: Decimal = field(default=Decimal("0"), repr=False)

    @property
    def items(self) -> tuple[OrderItem, ...]:
        return tuple(self._items)

    def add_item(self, item: OrderItem) -> None:
        if self.status != OrderStatus.PENDING:
            raise InvalidOrderError(
                "Can only add items to an order with status PENDING."
            )
        self._items.append(item)
        self.updated_at = datetime.now()

    @property
    def total_before_discount(self) -> Decimal:
        return sum((item.subtotal for item in self._items), Decimal("0"))

    @property
    def discount_amount(self) -> Decimal:
        return self._discount_amount

    def apply_discount(self, amount: Decimal) -> None:
        if amount < 0:
            raise InvalidOrderError("Discount amount cannot be negative.")
        if amount > self.total_before_discount:
            raise InvalidOrderError(
                "Discount amount cannot exceed the total before discount."
            )
        self._discount_amount = amount
        self.updated_at = datetime.now()

    @property
    def total_amount(self) -> Decimal:
        return self.total_before_discount - self._discount_amount
    
    def  validate_not_empty(self) -> None:
        if not self._items:
            raise InvalidOrderError("Order must have aleast one item.")

    def mark_completed(self) -> None:
        self.validate_not_empty()
        self.status = OrderStatus.COMPLETED
        self.updated_at = datetime.now()

    def cancel(self) -> None:
        self.status = OrderStatus.CANCELED
        self.updated_at = datetime.now()
        

