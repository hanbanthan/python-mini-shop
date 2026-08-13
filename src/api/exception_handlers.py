
import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from src.exceptions import (
    AppError,
    CustomerNotFoundError,
    DatabaseOperationError,
    InsufficientStockError,
    InvalidCustomerDataError,
    InvalidOrderError,
    InvalidProductDataError,
    ProductNotFoundError,
    OrderNotFoundError,
    UserInputError,
    DatabaseOperationError,
)

logger = logging.getLogger(__name__)

def _error_response(status_code: int, message: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"detail": message})


def _validation_message(request: Request, exc: RequestValidationError) -> str:
    errors = exc.errors()
    first_error = errors[0] if errors else {}
    field_path = first_error.get("loc", [])
    error_type = first_error.get("type", "")

    if request.url.path.startswith("/products") and "name" in field_path and error_type == "string_too_short":
        return "Invalid product data: name must not be empty."
    if request.url.path.startswith("/customers") and "full_name" in field_path and error_type == "string_too_short":
        return "Invalid customer data: full_name must not be empty."

    return first_error.get("msg", "Invalid request")

def register_exception_handlers(app: FastAPI) -> None:
    """Register exception handlers for the FastAPI applications.

    Call once time when call create_app(), not repeat in each route
    """

    @app.exception_handler(ProductNotFoundError)
    @app.exception_handler(CustomerNotFoundError)
    @app.exception_handler(OrderNotFoundError)
    async def handle_not_found_error(request: Request, exc: AppError) -> JSONResponse:
        return _error_response(404, str(exc))

    @app.exception_handler(InvalidProductDataError)
    @app.exception_handler(InvalidCustomerDataError)
    @app.exception_handler(InvalidOrderError)
    @app.exception_handler(UserInputError)
    async def handle_bad_request(request: Request, exc: AppError) -> JSONResponse:
        return _error_response(400, str(exc))

    @app.exception_handler(InsufficientStockError)
    async def handle_conflict(request: Request, exc: AppError) -> JSONResponse:
        return _error_response(409, str(exc))

    @app.exception_handler(DatabaseOperationError)
    async def handle_database_error(request: Request, exc: AppError) -> JSONResponse:
        # Log full error, not return detail DB error to response
        # hide the detail of table and SQL query to client
        logger.error(f"Database operation error: {exc}")
        return _error_response(500, "Error occurred while processing the request. Please try again later.")

    @app.exception_handler(RequestValidationError)
    async def handle_request_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        return _error_response(400, _validation_message(request, exc))

    @app.exception_handler(AppError)
    async def handle_generic_app_error(request: Request, exc: AppError) -> JSONResponse:
        # Fallback for other exception not map above - return 400 instead return 500 and traceback
        logger.warning(f"AppError not mapped to specific handler: {exc}")
        return _error_response(400, str(exc))
