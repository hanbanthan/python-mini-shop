import pytest

from src.exceptions import (
    AppError,
    ProductNotFoundError,
    InvalidProductDataError,
    InsufficientStockError,
    InvalidOrderError,
    CustomerNotFoundError,
    InvalidCustomerDataError,
    DatabaseOperationError,
    UserInputError,
)

ALL_EXCEPTIONS = [
    ProductNotFoundError,
    InvalidProductDataError,
    InsufficientStockError,
    InvalidOrderError,
    CustomerNotFoundError,
    InvalidCustomerDataError,
    DatabaseOperationError,
    UserInputError,
]


@pytest.mark.parametrize("exc_class", ALL_EXCEPTIONS)
def test_all_exceptions_inherit_from_app_error(exc_class):
    assert issubclass(exc_class, AppError)


def test_exception_carries_message():
    with pytest.raises(ProductNotFoundError) as exc_info:
        raise ProductNotFoundError("Test message")
    assert "Test message" in str(exc_info.value)


def test_app_error_can_catch_any_business_exception():
    with pytest.raises(AppError):
        raise InsufficientStockError("Insufficient stock for product.")
