<<<<<<< HEAD
""" Unit test cho Dicount Policy (Strategy + Factory Pattern) - thuan tinh 
=======
"""Unit test cho Dicount Policy (Strategy + Factory Pattern) - thuan tinh
>>>>>>> origin/main
toan, khong can DB, chay rat nhanh.
"""

from decimal import Decimal

import pytest

from src.models.enums import CustomerType
from src.patterns.discount.factory import DiscountPolicyFactory
<<<<<<< HEAD
from src.patterns.discount.regular_customer_discount import RegularCustomerDiscount 
from src.patterns.discount.vip_customer_discount import VIPCustomerDiscount

=======
from src.patterns.discount.regular_customer_discount import RegularCustomerDiscount
from src.patterns.discount.vip_customer_discount import VIPCustomerDiscount


>>>>>>> origin/main
def test_regular_discount_is_zero():
    policy = DiscountPolicyFactory.get_policy(CustomerType.REGULAR)
    assert isinstance(policy, RegularCustomerDiscount)
    assert policy.calculate_discount(Decimal("2000000")) == Decimal("0")

<<<<<<< HEAD
=======

>>>>>>> origin/main
def test_vip_customer_discount_small_order():
    policy = DiscountPolicyFactory.get_policy(CustomerType.VIP)
    assert isinstance(policy, VIPCustomerDiscount)
    assert policy.calculate_discount(Decimal("2000000")) == Decimal("200000")

<<<<<<< HEAD
=======

>>>>>>> origin/main
def test_vip_customer_discount_large_order():
    policy = DiscountPolicyFactory.get_policy(CustomerType.VIP)
    assert policy.calculate_discount(Decimal("6000000")) == Decimal("900000")

<<<<<<< HEAD
=======

>>>>>>> origin/main
def test_vip_customer_discount_boundary_exactly_threshold():
    policy = DiscountPolicyFactory.get_policy(CustomerType.VIP)
    assert policy.calculate_discount(Decimal("5000000")) == Decimal("500000")

<<<<<<< HEAD
@pytest.mark.parametrize("buggy_percent", [Decimal("30"), Decimal("100")])
def test_discount_always_capped_at_15_percent(buggy_percent):
    """ Gioi han giam gia toi da 15% - PHAI duoc ap dung du
=======

@pytest.mark.parametrize("buggy_percent", [Decimal("30"), Decimal("100")])
def test_discount_always_capped_at_15_percent(buggy_percent):
    """Gioi han giam gia toi da 15% - PHAI duoc ap dung du
>>>>>>> origin/main
    policy con tinh sai (gia lap loi lap trinh co y tra ve % vuot muc)
    """

    class BuggyPolicy(VIPCustomerDiscount):
        def _discount_percent(self, order_total: Decimal) -> Decimal:
            return buggy_percent
<<<<<<< HEAD
    
=======

>>>>>>> origin/main
    policy = BuggyPolicy()
    # 15% cua 10,000,000 = 1,500,000, bat ke buggy_percent la bao nhieu
    assert policy.calculate_discount(Decimal("10000000")) == Decimal("1500000")

<<<<<<< HEAD
def test_discount_policy_factory_returns_correct_class_per_type():
    assert type(DiscountPolicyFactory.get_policy(CustomerType.REGULAR)) is RegularCustomerDiscount
    assert type(DiscountPolicyFactory.get_policy(CustomerType.VIP)) is VIPCustomerDiscount

=======

def test_discount_policy_factory_returns_correct_class_per_type():
    assert type(DiscountPolicyFactory.get_policy(CustomerType.REGULAR)) is RegularCustomerDiscount
    assert type(DiscountPolicyFactory.get_policy(CustomerType.VIP)) is VIPCustomerDiscount
>>>>>>> origin/main
