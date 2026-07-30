from decimal import Decimal

from src.patterns.discount.base import DiscountPolicy

class RegularCustomerDiscount(DiscountPolicy):

    def _discount_percent(self, order_total: Decimal) -> Decimal:
        return Decimal("0")
