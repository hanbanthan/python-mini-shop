import logging

from src.patterns.observer.base import OrderCreatedEvent, OrderObserver

audit_logger = logging.getLogger("audit")

class AuditLogObserver(OrderObserver):
    def on_order_created(self, event: OrderCreatedEvent) -> None:
        audit_logger.info(
            "Order created: order_id=%s, customer_id=%s, customer_name=%s, total_before_discount=%.2f, discount_amount=%.2f, total_amount=%.2f, status=%s",
            event.order.id,
            event.customer.id,
            event.customer.full_name,
            event.order.total_before_discount,
            event.order.discount_amount,
            event.order.total_amount,
            event.order.status.value,
        )