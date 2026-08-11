import logging

from src.patterns.observer.base import OrderCreatedEvent, OrderObserver

logger = logging.getLogger("stock_update")


class StockUpdateObserver(OrderObserver):
    def on_order_created(self, event: OrderCreatedEvent) -> None:
        for item in event.order.items:
            logger.info(
                "Stock update for product_id=%s, quantity=%s, product_name=%s, order_id=%s",
                item.quantity,
                item.product_id,
                item.product_name_snapshot,
                event.order.id,
            )
