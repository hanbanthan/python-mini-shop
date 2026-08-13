
from datetime import datetime

from fastapi import APIRouter, Depends, Query, status

from src.api.dependencies import get_order_service
from src.api.schemas.order import (
    OrderCreateRequest,
    OrderListResponse,
    OrderResponse,
    order_to_response,
)
from src.models.enums import OrderStatus
from src.services.order_service import OrderService

router = APIRouter()

@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    payload: OrderCreateRequest,
    service: OrderService = Depends(get_order_service),
) -> OrderResponse:
    items = [(item.product_id, item.quantity) for item in payload.items]
    order = service.create_order(customer_id=payload.customer_id, items=items)
    return order_to_response(order)

@router.get("", response_model=OrderListResponse)
def list_orders(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    service: OrderService = Depends(get_order_service),
) -> OrderListResponse:
    orders, total_pages = service.list_orders_page(page=page, page_size=page_size)
    return OrderListResponse(
        items=[order_to_response(order) for order in orders],
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )

@router.get("/search", response_model=list[OrderResponse])
def search_orders(
    customer_id: int | None = None,
    order_status: OrderStatus | None = Query(default=None, alias="status"),
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    service: OrderService = Depends(get_order_service),
) -> list[OrderResponse]:
    """
    Query param ten `status` trong request, 
    vi `status` trung voi ten module fastpi.status da import o cac router khac cung package
    nhung trong code minh dat ten param la `order_status` 
    """
    orders = service.search_orders(
        customer_id=customer_id,
        status=order_status,
        date_from=date_from,
        date_to=date_to
    )
    return [order_to_response(order) for order in orders]

@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    service: OrderService = Depends(get_order_service),
) -> OrderResponse:
    order = service.get_order(order_id)
    return order_to_response(order)

