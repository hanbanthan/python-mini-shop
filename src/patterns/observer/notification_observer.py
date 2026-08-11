import logging

from src.patterns.observer.base import OrderCreatedEvent, OrderObserver

logger = logging.getLogger("notification")


class CustomerNotificationObserver(OrderObserver):
    def on_order_created(self, event: OrderCreatedEvent) -> None:
        message = (
            f"Notification: Order {event.order.id} has been created for customer "
            f"{event.customer.full_name} (ID: {event.customer.id})."
            f"Total amount: ${event.order.total_amount:.2f}"
        )
        logger.info(message)
        print(message)
