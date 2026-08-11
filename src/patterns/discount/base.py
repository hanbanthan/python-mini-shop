"""
Abstract base DiscountPolicy - Strategy Pattern

Why use Strategy Pattern:
- Each customer has different discount policy, the formula can be changed indepenedently
without changing OrderService
- OrderService only need to call policy.calculate_discount(order_total)
and do not need to know what type of customer
"""

from abc import ABC, abstractmethod
from decimal import Decimal

from src.config.settings import settings


class DiscountPolicy(ABC):
    """Interface + template method for all discount policy"""

    @abstractmethod
    def _discount_percent(self, order_total: Decimal) -> Decimal:
        """Return discount percent based on order_total"""

    def calculate_discount(self, order_total: Decimal) -> Decimal:
        """
        Calculate real discount -> always be limit by settings.max_discount_percent(15%),
        irrespective of policy's discount percent
        This is mutual method, not override
        """
        if order_total < 0:
            raise ValueError("order total cannot be negative")

        raw_percent = self._discount_percent(order_total)
        capped_percent = min(raw_percent, Decimal(str(settings.max_discount_percent)))
        capped_percent = max(capped_percent, Decimal("0"))

        discount_amount = (order_total * capped_percent / Decimal("100")).quantize(Decimal("1"))
        return discount_amount
