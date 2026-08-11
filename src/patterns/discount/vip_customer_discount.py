from decimal import Decimal

from src.config.settings import settings
from src.patterns.discount.base import DiscountPolicy


class VIPCustomerDiscount(DiscountPolicy):
    def _discount_percent(self, order_total: Decimal) -> Decimal:
        percent = Decimal(str(settings.vip_discount_percent))
        if order_total > Decimal(str(settings.large_order_threshold)):
            percent += Decimal(str(settings.large_order_extra_discount))
        return percent
