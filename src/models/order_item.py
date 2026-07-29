"""
Model OrderItem

Use dataclass because OrderItem is value object, used to store snapshot of 
at the time of order creation, no complex logic in this class
so dataclass + property is enough to implement this calss

Encapsulation: subtotal is calculated from quantity and unit price
, advoid the case when subtotal is assigned not correct quantity or price
"""

from dataclasses import dataclass
from decimal import Decimal

from src.exceptions import InvalidOrderError

@dataclass
class OrderItem:
    product_id: int
    product_name_snapshot: str
    quantity: int
    unit_price_snapshot: Decimal

    def __post_init__(self) -> None:
        if self.quantity <= 0:
            raise InvalidOrderError(
                f"Quantity of product {self.product} must be greater than 0"
            )
        if self.unit_price_snapshot<= 0:
            raise InvalidOrderError(
                f"Unit price of product {self.product} must be greatert than 0"
            )
    
    @property
    def subtotal(self) -> Decimal:
        return self.quantity * self.unit_price_snapshot