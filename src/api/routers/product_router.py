from decimal import Decimal
from fastapi import APIRouter, Depends, Query, status

from src.api.dependencies import get_product_service
from src.api.schemas.product import (
    ProductCreateRequest,
    ProductListResponse,
    ProductResponse,
    ProductUpdateRequest,
    product_to_response,
)
from src.services.product_service import ProductService

router = APIRouter()

@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    payload: ProductCreateRequest,
    service: ProductService = Depends(get_product_service),
) -> ProductResponse:
    product = service.add_product(
        name=payload.name,
        category=payload.category,
        price=payload.price,
        stock_quantity=payload.stock_quantity,
        tags=payload.tags,
    )
    return product_to_response(product)

@router.get("", response_model=ProductListResponse)
def list_products(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    service: ProductService = Depends(get_product_service),
) -> ProductListResponse:
    products, total_pages = service.list_products_page(page=page, page_size=page_size)
    return ProductListResponse(
        items=[product_to_response(product) for product in products],
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )

@router.get("/search", response_model=list[ProductResponse])
def search_products(
    keyword: str | None = None,
    category: str | None = None,
    min_price: Decimal | None = None,
    max_price: Decimal | None = None,
    tag: str | None = None,
    active_only: bool = False,
    service: ProductService = Depends(get_product_service),
) -> list[ProductResponse]:
    """DAT TRUOC `GET/{product_id}` trong router de khong bi nham
    'search' la 1 product_id (du FastAPI da tu phan biet dung qua 
    type converter 'int' cua 'product_id', dat ruoc van ro rang hon
    khi doc code).
    """
    products = service.search_products(
        keyword=keyword,
        category=category,
        min_price=min_price,
        max_price=max_price,
        tag=tag,
        active_only=active_only,
    )
    return [product_to_response(p) for p in products]

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    service: ProductService = Depends(get_product_service),
) -> ProductResponse:
    product = service.get_product(product_id=product_id)
    return product_to_response(product) 

@router.patch("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    payload: ProductUpdateRequest,
    service: ProductService = Depends(get_product_service),
) -> ProductResponse:
    product = service.update_product(
        product_id,
        name=payload.name,
        category=payload.category,
        price=payload.price,
        stock_quantity=payload.stock_quantity,
        tags=payload.tags,
    )
    return product_to_response(product)

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    service: ProductService = Depends(get_product_service),
) -> None:
    service.remove_product(product_id=product_id)

