from abc import ABC, abstractmethod
from dataclasses import dataclass

from src.models.customer import Customer
from src.models.order import Order


@dataclass(frozen=True)
class OrderCreatedEvent:
    order: Order
    customer: Customer


class OrderObserver(ABC):
    @abstractmethod
    def on_order_created(self, event: OrderCreatedEvent) -> None:
        pass
