
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from src.models.customer import Customer
from src.models.enums import CustomerType

class CustomerCreateRequest(BaseModel):
    full_name: str = Field(..., min_length=1, description="Full name of the customer")
    email: EmailStr = Field(..., description="Email must be unique")
    phone: str = Field(..., min_length=1, description="Phone number")
    customer_type: CustomerType = Field(default=CustomerType.REGULAR)

class CustomerUpdateRequest(BaseModel):
    full_name: str | None = Field(default=None, min_length=1)
    email: EmailStr | None = Field(default=None)
    phone: str | None = Field(default=None, min_length=1)

class CustomerTierUpdateRequest(BaseModel):
    """Body cho Patch /customers/{customer_id}/tier"""
    customer_type: CustomerType

class CustomerResponse(BaseModel):
    id: int
    full_name: str
    email: str
    phone: str
    customer_type: CustomerType
    created_at: datetime
    updated_at: datetime

class CustomerListResponse(BaseModel):
    items: list[CustomerResponse]
    page: int
    page_size: int
    total_pages: int

def customer_to_response(customer: Customer) -> CustomerResponse:
    return CustomerResponse(
        id=customer.id,
        full_name=customer.full_name,
        email=customer.email,
        phone=customer.phone,
        customer_type=customer.customer_type,
        created_at=customer.created_at,
        updated_at=customer.updated_at,
    )
    
