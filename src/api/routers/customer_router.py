
from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.api.dependencies import get_customer_service
from src.api.schemas.customer import (
    CustomerCreateRequest,
    CustomerListResponse,
    CustomerResponse,
    CustomerTierUpdateRequest,
    CustomerUpdateRequest,
    customer_to_response,
)
from src.exceptions import InvalidCustomerDataError
from src.models.enums import CustomerType
from src.services.customer_service import CustomerService

router = APIRouter()

@router.post("", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer(
    payload: CustomerCreateRequest,
    service: CustomerService = Depends(get_customer_service),
) -> CustomerResponse:
    customer = service.add_customer(
        full_name=payload.full_name,
        email=payload.email,
        phone=payload.phone,
        customer_type=payload.customer_type,
    )
    return customer_to_response(customer)

@router.get("", response_model=CustomerListResponse)
def list_customers(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    service: CustomerService = Depends(get_customer_service),
) -> CustomerListResponse:
    customers, total_pages = service.list_customers_page(page=page, page_size=page_size)
    return CustomerListResponse(
        items=[customer_to_response(customer) for customer in customers],
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )

@router.get("/search", response_model=list[CustomerResponse])
def search_customers(
    keyword: str | None = None,
    service: CustomerService = Depends(get_customer_service),
) -> list[CustomerResponse]:
    customers = service.search_customers(keyword=keyword)
    return [customer_to_response(customer) for customer in customers]

@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(
    customer_id: int,
    service: CustomerService = Depends(get_customer_service),
) -> CustomerResponse:
    customer = service.get_customer(customer_id)
    return customer_to_response(customer)

@router.patch("/{customer_id}", response_model=CustomerResponse)
def update_customer(
    customer_id: int,
    payload: CustomerUpdateRequest,
    service: CustomerService = Depends(get_customer_service),
) -> CustomerResponse:
    customer = service.update_customer(
        customer_id,
        full_name=payload.full_name,
        email=payload.email,
        phone=payload.phone,
    )
    return customer_to_response(customer)

@router.patch("/{customer_id}/tier", response_model=CustomerResponse)
def update_customer_tier(
    customer_id: int,
    payload: CustomerTierUpdateRequest,
    service: CustomerService = Depends(get_customer_service),
) -> CustomerResponse:
    if payload.customer_type == CustomerType.VIP:
        customer = service.upgrade_customer_to_vip(customer_id)
    else:
        customer = service.downgrade_customer_to_regular(customer_id)
    return customer_to_response(customer)

@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(
    customer_id: int,
    service: CustomerService = Depends(get_customer_service),
) -> None:
    try:
        service.remove_customer(customer_id)
    except InvalidCustomerDataError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc



