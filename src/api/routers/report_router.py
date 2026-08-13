
import tempfile
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, Query
from fastapi.responses import FileResponse

from src.api.dependencies import get_report_service
from src.api.schemas.report import (
    BestSellingProductResponse,
    RevenueSummaryResponse,
    TopCustomerResponse,
    TopOrderResponse,
)
from src.services.report_service import ReportService

router = APIRouter()

@router.get("/summary", response_model=RevenueSummaryResponse)
def get_revenue_summary(
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    service: ReportService = Depends(get_report_service),
) -> RevenueSummaryResponse:
    summary = service.revenue_summary(date_from=date_from, date_to=date_to)
    return RevenueSummaryResponse(**summary)

@router.get("/best-seller", response_model=list[BestSellingProductResponse])
def get_best_sellers(
    limit: int = Query(default=5, ge=1, le=50),
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    service: ReportService = Depends(get_report_service),
) -> list[BestSellingProductResponse]:
    items = service.best_selling_products(limit=limit, date_from=date_from, date_to=date_to)
    return [BestSellingProductResponse(**item) for item in items]

@router.get("/by-category", response_model=dict[str, Decimal])
def get_revenue_by_category(
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    service: ReportService = Depends(get_report_service),
) -> dict:
    return service.revenue_by_category(date_from=date_from, date_to=date_to)

@router.get("/by-day", response_model=dict[str, Decimal])
def get_revenue_by_day(
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    service: ReportService = Depends(get_report_service),
) -> dict:
    return service.revenue_by_day(date_from=date_from, date_to=date_to)

@router.get("/by-month", response_model=dict[str, Decimal])
def get_revenue_by_month(
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    service: ReportService = Depends(get_report_service),
) -> dict:
    return service.revenue_by_month(date_from=date_from, date_to=date_to)

@router.get("/top-customers", response_model=list[TopCustomerResponse])
def get_top_customers(
    limit: int = Query(default=5, ge=1, le=50),
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    service: ReportService = Depends(get_report_service),
) -> list[TopCustomerResponse]:
    items = service.top_customers(limit=limit, date_from=date_from, date_to=date_to)
    return [TopCustomerResponse(**item) for item in items]

@router.get("/export.csv")
def export_report_csv(
    background_tasks: BackgroundTasks,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    service: ReportService = Depends(get_report_service),
) -> FileResponse:
    """
    Tra file CSV tai ve truc tiep

    Ghi ra file tam thoi tempfile, thay vi thu muc export cua CLI, khogn dung file cua nhau.
    file tam duoc xoa ngay sau khi response da gui xong
    """
    tmp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False)
    tmp_file.close()

    filepath = service.export_to_csv(file_path=Path(tmp_file.name), date_from=date_from, date_to=date_to)
    background_tasks.add_task(lambda: Path(filepath).unlink(missing_ok=True))

    return FileResponse(
        path=filepath,
        media_type="text/csv",
        filename="revenue_report.csv",
    )


