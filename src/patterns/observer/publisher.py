import logging

from src.patterns.observer.base import OrderCreatedEvent, OrderObserver

logger = logging.getLogger(__name__)


class OrderEventPublisher:
    def __init__(self) -> None:
        self._observers: list[OrderObserver] = []

    def subscribe(self, observer: OrderObserver) -> None:
        self._observers.append(observer)

    def unsubscribe(self, observer: OrderObserver) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, event: OrderCreatedEvent) -> None:
        for observer in self._observers:
            try:
                observer.on_order_created(event)
            except Exception as exc:
                logger.error(
                    f"Error notifying observer {observer.__class__.__name__}: {exc}",
                )
