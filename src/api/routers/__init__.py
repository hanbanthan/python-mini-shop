from fastapi import APIRouter

from src.api.routers.customer_router import router as customer_router
from src.api.routers.order_router import router as order_router
from src.api.routers.product_router import router as product_router
from src.api.routers.report_router import router as report_router

router = APIRouter()

router.include_router(product_router, prefix="/products", tags=["products"])
router.include_router(customer_router, prefix="/customers", tags=["customers"])
router.include_router(order_router, prefix="/orders", tags=["orders"])
router.include_router(report_router, prefix="/reports", tags=["reports"])
