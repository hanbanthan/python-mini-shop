"""
DiscountPolicyFactory - Factory Pattern

Why use Factory pattern?
- Orderservice need 1 discount policy for each CustomerType 
but should not use if else to choose
- When add new type of customer, only one line new  policy_map,
do not need to change OrderService
"""

from src.exceptions import InvalidCustomerDataError
from src.models.enums import CustomerType
from src.patterns.discount.base import DiscountPolicy
from src.patterns.discount.regular_customer_discount import RegularCustomerDiscount
from src.patterns.discount.vip_customer_discount import VIPCustomerDiscount

class DiscountPolicyFactory:
    
    _POLICY_MAP: dict[CustomerType, type[DiscountPolicy]] = {
        CustomerType.REGULAR: RegularCustomerDiscount,
        CustomerType.VIP: VIPCustomerDiscount,
    }

    @classmethod
    def get_policy(cls, customer_type: CustomerType) -> DiscountPolicy:
        policy_class = cls._POLICY_MAP.get(customer_type)
        if policy_class is None:
            raise InvalidCustomerDataError(f"No discount policy for customer type {customer_type}")
        return policy_class()

