from enum import StrEnum


class ProductStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class CustomerType(StrEnum):
    REGULAR = "regular"
    VIP = "vip"


class OrderStatus(StrEnum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
