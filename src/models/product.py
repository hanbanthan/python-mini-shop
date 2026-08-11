"""
Use @dataclass because Product is mainly used for data storage (id, name, price,...)
there is no complex logic in this class, so using dataclass reduce boilerplate code (__init__, __repr__, __eq___)
and still can add method if needed in the future

Encapsulation: stock_quantity can not be modified dirrectly from outside,
(product.stock_quantity=10) is not allowed. Every modification of stock
must go through the method to ensure the stock quantity is always valid
not negative and not exeeding the maximum stock quantity
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal

from src.exceptions import InsufficientStockError, InvalidProductDataError

from .enums import ProductStatus


@dataclass
class Product:
    id: int | None
    name: str
    category: str
    price: Decimal
    tags: set[str] = field(default_factory=set)
    status: ProductStatus = ProductStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    # field private attribute to prevent direct modification from outside class
    _stock_quantity: int = field(default=0, repr=False)

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise InvalidProductDataError("Product name can not be empty")
        if self.price < 0:
            raise InvalidProductDataError("Product price can not be negative")
        if self._stock_quantity < 0:
            raise InvalidProductDataError("Product stock quantity can not be negative")

    @property
    def stock_quantity(self) -> int:
        return self._stock_quantity

    @property
    def is_active(self) -> bool:
        return self.status == ProductStatus.ACTIVE

    def reduce_stock(self, quantity: int) -> None:
        if quantity < 0:
            raise InvalidProductDataError("Quantity to reduce can not be negative")
        if quantity > self.stock_quantity:
            raise InsufficientStockError(
                f"Product {self.name} has insufficient stock. "
                f"(Current stock: {self.stock_quantity}, need {quantity})"
            )
        self._stock_quantity -= quantity
        self.updated_at = datetime.now()

    def increase_stock(self, quantity: int) -> None:
        if quantity < 0:
            raise InvalidProductDataError("Quantity to increase can not be negative")
        self._stock_quantity += quantity
        self.updated_at = datetime.now()

    def deactivate(self) -> None:
        """Deactivate the product, to maintain transaction history"""
        self.status = ProductStatus.INACTIVE
        self.updated_at = datetime.now()
