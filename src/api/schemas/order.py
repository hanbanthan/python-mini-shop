
from datetime import datetime
from decimal import Decimal 

from pydantic import BaseModel, Field

from src.models.enums import OrderStatus
from src.models.order import Order
from src.models.order_item import OrderItem

class OrderItemCreateRequest(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0, description="Quantity must be greater than 0")

class OrderCreateRequest(BaseModel):
    customer_id: int = Field(..., gt=0)
    items: list[OrderItemCreateRequest] = Field(..., min_length=1, description="Order must contain at least 1 item")

class OrderItemResponse(BaseModel):
    product_id: int
    product_name_snapshot: str
    quantity: int
    unit_price_snapshot: Decimal
    subtotal: Decimal

class OrderResponse(BaseModel):
    id: int
    customer_id: int
    status: OrderStatus
    items: list[OrderItemResponse]
    total_before_discount: Decimal
    discount_amount: Decimal
    total_amount: Decimal
    created_at: datetime
    updated_at: datetime

class OrderListResponse(BaseModel):
    items: list[OrderResponse]
    page: int
    page_size: int
    total_pages: int

def order_to_response(order: Order) -> OrderResponse:
    return OrderResponse(
        id=order.id,
        customer_id=order.customer_id,
        status=order.status,
        items=[_order_item_to_response(item) for item in order.items],
        total_before_discount=order.total_before_discount,
        discount_amount=order.discount_amount,
        total_amount=order.total_amount,
        created_at=order.created_at,
        updated_at=order.updated_at,
    )

def _order_item_to_response(item: OrderItem) -> OrderItemResponse:
    return OrderItemResponse(
        product_id=item.product_id,
        product_name_snapshot=item.product_name_snapshot,
        quantity=item.quantity,
        unit_price_snapshot=item.unit_price_snapshot,
        subtotal=item.subtotal,
    )