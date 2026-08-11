"""
Observer ghi audit log khi tao don hang thanh cong

Ghi ra ca 2 noi (nang cao - audit log rieng biet):
1. Logger "audit" -> ghi ra file logs/audit.log (cau hinh o
src/config/logging_config.py) - doc nhanh dang text, tuan tu.
2. Bang audit_log trong DB (qua AuditLogRepository) - truy van duoc

1 trong 2 sink loi khong duoc lam hong cai con lai - moi sinh tu bat loi
rieng cua minh (OrderEventPublisher cung co lop bao ve o tang ngoai nua)
"""

import logging

from src.exceptions import DatabaseOperationError
from src.patterns.observer.base import OrderCreatedEvent, OrderObserver
from src.repositories.audit_log_repository import AuditLogRepository

audit_logger = logging.getLogger("audit")


class AuditLogObserver(OrderObserver):
    def __init__(self, audit_log_repository: AuditLogRepository | None = None) -> None:
        self._repo = audit_log_repository or AuditLogRepository()

    def on_order_created(self, event: OrderCreatedEvent) -> None:
        details = (
            f"order_id={event.order.id} "
            f"customer_id={event.order.customer_id} "
            f"total_before_discount={event.order.total_before_discount} "
            f"discount_amount={event.order.discount_amount} "
            f"total_amount={event.order.total_amount} "
        )

        # Sink 1: file log
        audit_logger.info("Order created: %s", details)

        # Sink 2: Bang DB - bat rieng DatabaseOperationError de sink 1 van
        # coi nhu thanh cong du sink 2 loi (vd: DB tam thoi ban)
        try:
            self._repo.add_entry(
                event_type="order_created",
                details=details,
                order_id=event.order.id,
                customer_id=event.order.customer_id,
            )
        except DatabaseOperationError as e:
            audit_logger.error("Failed to write to audit log DB: %s", str(e))
