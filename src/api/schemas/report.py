
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

class RevenueSummaryResponse(BaseModel):
    total_before_discount: Decimal
    total_discount: Decimal
    total_revenue: Decimal

class BestSellingProductResponse(BaseModel):
    product_id: int
    product_name: str
    total_quantity: int

class TopOrderResponse(BaseModel):
    order_id: int
    customer_id: int
    total_amount: Decimal
    created_at: datetime

class TopCustomerResponse(BaseModel):
    customer_id: int
    full_name: str
    total_spent: Decimal
    