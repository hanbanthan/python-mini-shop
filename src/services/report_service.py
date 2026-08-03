from datetime import datetime
from decimal import Decimal

from src.repositories.report_repository import ReportRepository

class ReportService:
    def __init__(self, report_repository: ReportRepository | None = None) -> None:
        self._repo = report_repository or ReportRepository()
    
    def total_orders(
        self, date_from: datetime | None = None, date_to: datetime | None = None
    ) -> int:
        return self._repo.count_orders(date_from=date_from, date_to=date_to)
    
    def revenue_summary(
        self,
        date_from: datetime | None = None,
        date_to: datetime | None = None
    ) -> dict[str, Decimal]:
        return self._repo.revenue_summary(date_from=date_from, date_to=date_to)
    
    def best_selling_products(
        self,
        limit: int = 5,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> list[dict]:
        return self._repo.best_selling_products(limit=limit, date_from=date_from, date_to=date_to)
    
    def revenue_by_category(
        self, date_from: datetime | None = None, date_to: datetime | None = None
    ) -> dict[str, Decimal]:
        return self._repo.revenue_by_category(date_from=date_from, date_to=date_to)
    
    def revenue_by_day(
        self, date_from: datetime | None = None, date_to: datetime | None = None
    ) -> dict[str, Decimal]:
        return self._repo.revenue_by_day(date_from=date_from, date_to=date_to)
    
    def revenue_by_month(
        self, date_from: datetime | None = None, date_to: datetime | None = None
    ) -> dict[str, Decimal]:
        return self._repo.revenue_by_month(date_from=date_from, date_to=date_to)

    def average_order_value(
        self, date_from: datetime | None = None, date_to: datetime | None = None 
    ) -> Decimal:
        order_count = self.total_orders(date_from=date_from, date_to=date_to)
        if order_count == 0:
            return Decimal("0.00")
        summary = self.revenue_summary(date_from=date_from, date_to=date_to)
        return (summary["total_revenue"] / Decimal(order_count)).quantize(Decimal("1.00"))

    def top_orders(
        self,
        limit: int = 5,
        date_from: datetime | None = None,
        date_to: datetime | None = None
    ) -> list[dict]:
        return self._repo.top_orders(limit=limit, date_from=date_from, date_to=date_to)
    
    def top_customers(
        self,
        limit: int = 5,
        date_from: datetime | None = None,
        date_to: datetime | None = None
    ) -> list[dict]:
        return self._repo.top_customers_by_spending(limit=limit, date_from=date_from, date_to=date_to)


    def full_report(
        self,
        limit: int = 5,
        date_from: datetime | None = None,
        date_to: datetime | None = None
    ) -> dict:
        return {
            "total_orders": self.total_orders(date_from, date_to),
            "revenue_summary": self.revenue_summary(date_from, date_to),
            "average_order_value": self.average_order_value(date_from, date_to),
            "best_selling_products": self.best_selling_products(5, date_from, date_to),
            "revenue_by_category": self.revenue_by_category(date_from, date_to),
            "revenue_by_day": self.revenue_by_day(date_from, date_to),
            "top_orders": self.top_orders(5, date_from, date_to),
            "top_customers": self.top_customers(5, date_from, date_to),
        }