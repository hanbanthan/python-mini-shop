
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from src.models.product import Product

class ProductCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, description="Name of the product")
    category: str = Field(..., min_length=1, description="Category of the product")
    price: Decimal = Field(..., gt=0, description="Price of the product")
    stock_quantity: int = Field(default=0, ge=0, description="Stock quantity of the product first time")
    tags: set[str] = Field(default_factory=set, description="Tags associated with the product")

class ProductUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1)
    category: str | None = Field(default=None, min_length=1)
    price: Decimal | None = Field(default=None, gt=0)
    stock_quantity: int | None = Field(default=None, ge=0)
    tags: set[str] | None = None

class ProductResponse(BaseModel):
    id: int
    name: str
    category: str
    price: Decimal
    stock_quantity: int
    tags: set[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

class ProductListResponse(BaseModel):
    items: list[ProductResponse]
    page: int
    page_size: int
    total_pages: int

def product_to_response(product: Product) -> ProductResponse:
    return ProductResponse(
        id=product.id,
        name=product.name,
        category=product.category,
        price=product.price,
        stock_quantity=product.stock_quantity,
        tags=product.tags,
        is_active=product.is_active,
        created_at=product.created_at,
        updated_at=product.updated_at,
    )
