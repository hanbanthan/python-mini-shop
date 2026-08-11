"""
Model Customer

Use dataclass because Customer is mainly used for data storage, no complex logic in this class
Use __post__init to validate the data after initialization



"""

import re
from dataclasses import dataclass, field
from datetime import datetime

from src.exceptions import InvalidCustomerDataError
from src.models.enums import CustomerType

_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass
class Customer:
    id: int | None
    full_name: str
    email: str
    phone: str
    customer_type: CustomerType = CustomerType.REGULAR
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        if not self.full_name or not self.full_name.strip():
            raise InvalidCustomerDataError("Customer name can not be empty.")
        if not _EMAIL_PATTERN.match(self.email):
            raise InvalidCustomerDataError(f"Invalid email: {self.email}")
        if not self.phone or not self.phone.strip():
            raise InvalidCustomerDataError("Customer phone can not be empty.")

    @property
    def is_vip(self) -> bool:
        return self.customer_type == CustomerType.VIP

    def upgrade_to_vip(self) -> None:
        self.customer_type = CustomerType.VIP
        self.updated_at = datetime.now()
