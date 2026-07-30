"""

python -m scripts.manual_test_discount
"""

from decimal import Decimal

from src.models.enums import CustomerType
from src.patterns.discount.factory import DiscountPolicyFactory
from src.patterns.discount.regular_customer_discount import RegularCustomerDiscount
from src.patterns.discount.vip_customer_discount import VIPCustomerDiscount

def check(label: str, actual: Decimal, expected: Decimal) -> None:
    status = "OK" if actual == expected else "FAIL"
    print(f"[{status}] {label}: actual={actual}. expected={expected}")
    assert actual == expected, f"{label} failed"

def main() -> None:
    # 1 regular customer -> 0%
    regular_policy = DiscountPolicyFactory.get_policy(CustomerType.REGULAR)
    assert isinstance(regular_policy, RegularCustomerDiscount)
    check(
        "Regular customer discount for order total 1000000",
        regular_policy.calculate_discount(Decimal("1000000")),
        Decimal("0"),
    )

    # 2 VIP, small order -> 10%
    vip_policy = DiscountPolicyFactory.get_policy(CustomerType.VIP)
    assert isinstance(vip_policy, VIPCustomerDiscount)
    check(
        "VIP customer discount for order total 500000",
        vip_policy.calculate_discount(Decimal("500000")),
        Decimal("50000"),
    )

    # 3 VIP,large order -> 15%
    check(
        "VIP customer discount for order total 6000000",
        vip_policy.calculate_discount(Decimal("6000000")),
        Decimal("900000"),
    )

    # 4 VIP, over threshold -> 10%
    check(
        "VIP customer discount for order total 5000000",
        vip_policy.calculate_discount(Decimal("5000000")),
        Decimal("500000"),
    )

    # 5 Test limit 15% is applied even when 1 policy wrongly calculated bigger than 15%
    class BuggyOverDiscount(VIPCustomerDiscount):
        def _discount_percent(self, order_total: Decimal) -> Decimal:
            return Decimal("30")
    
    buggy_policy = BuggyOverDiscount()
    check(
        "Error Policy calculated 30% on order of 10,000,000 -> still assigned 15%",
        buggy_policy.calculate_discount(Decimal("10000000")),
        Decimal("1500000")
    )

    # 6 Factory return correct policy for each customer type
    assert DiscountPolicyFactory.get_policy(CustomerType.REGULAR).__class__ is RegularCustomerDiscount
    assert DiscountPolicyFactory.get_policy(CustomerType.VIP).__class__ is VIPCustomerDiscount

    print("All tests passed!")

if __name__ == "__main__":
    main()
