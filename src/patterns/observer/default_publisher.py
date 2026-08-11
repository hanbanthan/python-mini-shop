from src.patterns.observer.audit_log_observer import AuditLogObserver
from src.patterns.observer.notification_observer import CustomerNotificationObserver
from src.patterns.observer.publisher import OrderEventPublisher
from src.patterns.observer.stock_update_observer import StockUpdateObserver


def build_default_order_event_publisher() -> OrderEventPublisher:
    publisher = OrderEventPublisher()
    publisher.subscribe(AuditLogObserver())
    publisher.subscribe(CustomerNotificationObserver())
    publisher.subscribe(StockUpdateObserver())
    return publisher
