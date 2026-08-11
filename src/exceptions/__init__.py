class AppError(Exception):
    """Base exeption for the application."""


class ProductNotFoundError(AppError):
    """Exception raised when a product is not found in the database."""


class InvalidProductDataError(AppError):
    """Exception raised when the product data is invalid or incomplete."""


class InsufficientStockError(AppError):
    """Exception raised when there is not enough stock for a product."""


class InvalidOrderError(AppError):
    """Exception raised when an order is invalid or cannot be processed."""


class CustomerNotFoundError(AppError):
    """Exception raised when a customer is not found in the database."""


class InvalidCustomerDataError(AppError):
    """Exception raised when the customer data is invalid or incomplete."""


class DatabaseOperationError(AppError):
    """Exception raised when there is an error during a database operation."""


class UserInputError(AppError):
    """Exception raised when the user input is invalid or cannot be processed."""
