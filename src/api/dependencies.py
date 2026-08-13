"""FastAPI dependecy providers

Recycle constructor injection already in Service layer

Each request creates a new Service instance; which is not costly as
Repository inside each Service is still use 1 'DatabaseConnection' Singleton
- not open new connection each time

Use in route like:
    @router.get("/products/{product_id}")
    def get_product(
        product_id: int,
        service: ProductService = Depends(get_product_service),
    ):

"""

from src.services.customer_service import CustomerService
from src.services.order_service import OrderService
from src.services.product_service import ProductService
from src.services.report_service import ReportService

def get_product_service() -> ProductService:
    return ProductService()

def get_customer_service() -> CustomerService:
    return CustomerService()

def get_order_service() -> OrderService:
    return OrderService()

def get_report_service() -> ReportService:
    return ReportService()

