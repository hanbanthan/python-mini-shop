from datetime import datetime
from decimal import Decimal

from src.repositories.report_repository import ReportRepository


class ReportService:
    def __init__(self, report_repository: ReportRepository | None = None) -> None:
        self._repo = report_repository or ReportRepository()

    @staticmethod
    def _parse_date(value: str | datetime | None) -> datetime | None:
        if value is None or value == "":
            return None
        if isinstance(value, datetime):
            return value
        return datetime.strptime(value, "%Y-%m-%d")

    def total_orders(
        self, date_from: datetime | None = None, date_to: datetime | None = None
    ) -> int:
        return self._repo.count_orders(date_from=date_from, date_to=date_to)

    def revenue_summary(
        self, date_from: datetime | None = None, date_to: datetime | None = None
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
        self, limit: int = 5, date_from: datetime | None = None, date_to: datetime | None = None
    ) -> list[dict]:
        return self._repo.top_orders(limit=limit, date_from=date_from, date_to=date_to)

    def top_customers(
        self, limit: int = 5, date_from: datetime | None = None, date_to: datetime | None = None
    ) -> list[dict]:
        return self._repo.top_customers_by_spending(
            limit=limit, date_from=date_from, date_to=date_to
        )

    def date_range_report(
        self,
        date_from: str | datetime | None = None,
        date_to: str | datetime | None = None,
        limit: int = 5,
    ) -> dict:
        return self.full_report(
            limit=limit,
            date_from=self._parse_date(date_from),
            date_to=self._parse_date(date_to),
        )

    def _build_report(
        self,
        limit: int = 5,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> dict:
        summary = self.revenue_summary(date_from=date_from, date_to=date_to)
        return {
            "total_orders": self.total_orders(date_from=date_from, date_to=date_to),
            "revenue_summary": {
                **summary,
                "average_order_value": self.average_order_value(
                    date_from=date_from, date_to=date_to
                ),
            },
            "best_selling_products": self.best_selling_products(
                limit=limit, date_from=date_from, date_to=date_to
            ),
            "revenue_by_category": [
                {"category": category, "total_revenue": revenue}
                for category, revenue in self.revenue_by_category(
                    date_from=date_from, date_to=date_to
                ).items()
            ],
            "revenue_by_day": [
                {"date": date, "total_revenue": revenue}
                for date, revenue in self.revenue_by_day(
                    date_from=date_from, date_to=date_to
                ).items()
            ],
            "top_orders": self.top_orders(limit=limit, date_from=date_from, date_to=date_to),
            "top_customers": [
                {
                    "customer_id": customer["customer_id"],
                    "customer_name": customer["full_name"],
                    "total_spending": customer["total_spent"],
                }
                for customer in self.top_customers(
                    limit=limit, date_from=date_from, date_to=date_to
                )
            ],
        }

    def full_report(
        self, limit: int = 5, date_from: datetime | None = None, date_to: datetime | None = None
    ) -> dict:
        return self._build_report(limit=limit, date_from=date_from, date_to=date_to)

    def export_to_csv(
        self,
        file_path: str,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> str:
        """Nang cao Export bao cao ra file CSV. dung module csv buillt-in,
        khong can them dependency ngoai. Ghi nhieu section (tong quan,
        best-seller, doanh thu theo danh muc, theo ngay, top don/khach
        hang) trong cung 1 file CSV, phan cach bang dong trong + tieu de

        Tra ve duong dan file da ghi (de CLI/log hien thi lai)
        """
        import csv

        report = self.full_report(date_from=date_from, date_to=date_to)

        with open(file_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)

            writer.writerow(["REPORT SUMMARY"])
            writer.writerow(["Total Orders", report["total_orders"]])
            writer.writerow(
                ["Total before discount", report["revenue_summary"]["total_before_discount"]]
            )
            writer.writerow(["Total discount", report["revenue_summary"]["total_discount"]])
            writer.writerow(["Total revenue", report["revenue_summary"]["total_revenue"]])
            writer.writerow(
                ["Average Order Value", report["revenue_summary"]["average_order_value"]]
            )

            writer.writerow([])
            writer.writerow(["BEST SELLING PRODUCTS"])
            writer.writerow(["Product Name", "Quantity Sold"])
            for item in report["best_selling_products"]:
                writer.writerow([item["product_name"], item["total_quantity"]])

            writer.writerow([])
            writer.writerow(["REVENUE BY CATEGORY"])
            writer.writerow(["Category", "Total Revenue"])
            for item in report["revenue_by_category"]:
                writer.writerow([item["category"], item["total_revenue"]])

            writer.writerow([])
            writer.writerow(["REVENUE BY DAY"])
            writer.writerow(["Date", "Total Revenue"])
            for item in report["revenue_by_day"]:
                writer.writerow([item["date"], item["total_revenue"]])

            writer.writerow([])
            writer.writerow(["TOP ORDERS"])
            writer.writerow(["Order ID", "Total Amount"])
            for order_info in report["top_orders"]:
                writer.writerow([order_info["order_id"], order_info["total_amount"]])

            writer.writerow([])
            writer.writerow(["TOP CUSTOMERS"])
            writer.writerow(["Customer Name", "Total Spending"])
            for customer_info in report["top_customers"]:
                writer.writerow([customer_info["customer_name"], customer_info["total_spending"]])

        return file_path
