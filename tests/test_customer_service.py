import pytest

from src.exceptions import CustomerNotFoundError, InvalidCustomerDataError
from src.models.enums import CustomerType

def test_add_customer_valid(make_customer):
    customer = make_customer(full_name="Nguyen Van A")
    assert customer.id is not None
    assert customer.customer_type == CustomerType.REGULAR

def test_add_customer_duplicate_email_rejected(make_customer):
    make_customer(email="dup@example.com")
    with pytest.raises(InvalidCustomerDataError):
        make_customer(email="dup@example.com")

def test_add_customer_invalid_email_format(customer_service):
    with pytest.raises(InvalidCustomerDataError):
        customer_service.add_customer(full_name="Bad", email="not-an-email", phone="1234567890")

def test_add_customer_invalid_name_empty(customer_service):
    with pytest.raises(InvalidCustomerDataError):
        customer_service.add_customer(full_name=" ", email="ok@example.com", phone="1234567890")
    
def test_get_customer_found(customer_service, make_customer):
    customer = make_customer()
    found = customer_service.get_customer(customer.id)
    assert found.email == customer.email

def test_get_customer_not_found(customer_service):
    with pytest.raises(CustomerNotFoundError):
        customer_service.get_customer(999999)

def test_upgrade_to_vip(customer_service, make_customer):
    customer = make_customer()
    updated = customer_service.upgrade_to_vip(customer.id)
    assert updated.customer_type == CustomerType.VIP

def test_downgrade_to_regular(customer_service, make_customer):
    customer = make_customer(customer_type=CustomerType.VIP)
    updated = customer_service.downgrade_to_regular(customer.id)
    assert updated.customer_type == CustomerType.REGULAR

def test_search_customers_by_keyword(customer_service, make_customer):
    make_customer(full_name="Nguyen Van A", email="vana.search@example.com")
    make_customer(full_name="Tran Thi B", email="tranb.search@example.com")

    results = customer_service.search_customers(keyword="nguyen van")
    assert len(results) == 1
    assert results[0].full_name == "Nguyen Van A"

def test_remove_customer_without_orders_succeeds(customer_service, make_customer):
    customer = make_customer()
    customer_service.remove_customer(customer.id)
    with pytest.raises(CustomerNotFoundError):
        customer_service.get_customer(customer.id)

def test_remove_customer_with_orders_blocked(
    customer_service, order_service, make_customer, make_product
):
    customer = make_customer()
    product = make_product(stock=5)
    order_service.create_order(customer.id, [(product.id, 1)])
    with pytest.raises(InvalidCustomerDataError):
        customer_service.remove_customer(customer.id)


