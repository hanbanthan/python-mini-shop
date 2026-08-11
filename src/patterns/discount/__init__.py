from src.patterns.discount.base import DiscountPolicy
from src.patterns.discount.factory import DiscountPolicyFactory
from src.patterns.discount.regular_customer_discount import RegularCustomerDiscount
from src.patterns.discount.vip_customer_discount import VIPCustomerDiscount

__all__ = [
    "DiscountPolicy",
    "DiscountPolicyFactory",
    "RegularCustomerDiscount",
    "VIPCustomerDiscount",
]
