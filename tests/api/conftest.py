from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
import pytest

from src.api.dependencies import (
    get_customer_service,
    get_order_service,
    get_product_service,
    get_report_service,
)
from src.api.routers.customer_router import router as customer_router
from src.api.routers.order_router import router as order_router
from src.api.routers.product_router import router as product_router
from src.api.routers.report_router import router as report_router
from src.exceptions import (
    CustomerNotFoundError,
    InsufficientStockError,
    InvalidCustomerDataError,
    InvalidOrderError,
    InvalidProductDataError,
    OrderNotFoundError,
    ProductNotFoundError,
    UserInputError,
)
from src.patterns.observer.publisher import OrderEventPublisher
from src.services.customer_service import CustomerService
from src.services.order_service import OrderService
from src.services.product_service import ProductService
from src.services.report_service import ReportService

def _register_test_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ProductNotFoundError)
    @app.exception_handler(CustomerNotFoundError)
    @app.exception_handler(OrderNotFoundError)
    async def handle_not_found(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(InvalidProductDataError)
    @app.exception_handler(InvalidCustomerDataError)
    @app.exception_handler(InvalidOrderError)
    @app.exception_handler(UserInputError)
    async def handle_bad_request(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    @app.exception_handler(InsufficientStockError)
    async def handle_insufficient_stock(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        errors = exc.errors()
        first_error = errors[0] if errors else {}
        field_path = first_error.get("loc", [])
        error_type = first_error.get("type", "")

        if request.url.path.startswith("/products") and "name" in field_path and error_type == "string_too_short":
            message = "Invalid product data: name must not be empty."
        elif request.url.path.startswith("/customers") and "full_name" in field_path and error_type == "string_too_short":
            message = "Invalid customer data: full_name must not be empty."
        else:
            message = first_error.get("msg", "Invalid request")

        return JSONResponse(status_code=400, content={"detail": message})

def _build_test_app() -> FastAPI:
    app = FastAPI(title="Mini Store Management API")
    _register_test_exception_handlers(app)

    app.include_router(product_router, prefix="/products", tags=["Products"])
    app.include_router(customer_router, prefix="/customers", tags=["Customers"])
    app.include_router(order_router, prefix="/orders", tags=["Orders"])
    app.include_router(report_router, prefix="/reports", tags=["Reports"])
    return app

@pytest.fixture()
def api_client(test_db):
    app = _build_test_app()

    app.dependency_overrides[get_product_service] = lambda: ProductService()
    app.dependency_overrides[get_customer_service] = lambda: CustomerService()
    app.dependency_overrides[get_report_service] = lambda: ReportService()
    app.dependency_overrides[get_order_service] = lambda: OrderService(order_event_publisher=OrderEventPublisher())

    with TestClient(app) as client:
        yield client
    
    app.dependency_overrides.clear()

