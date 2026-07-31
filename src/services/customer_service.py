from datetime import datetime

from src.exceptions import InvalidCustomerDataError
from src.models.customer import Customer
from src.models.enums import CustomerType
from src.repositories.customer_repository import CustomerRepository

class CustomerService:
    def __init__(self, customer_repository: CustomerRepository | None = None) -> None:
        self._repo = customer_repository or CustomerRepository()

    def add_customer(
        self,
        full_name: str,
        email: str,
        phone: str,
        customer_type: CustomerType = CustomerType.REGULAR,
    ) -> Customer:
        if self._repo.get_by_email(email) is not None:
            raise InvalidCustomerDataError(f"Customer with email {email} already exists")
    
        customer = Customer(
            id=None, full_name=full_name, email=email, phone=phone, customer_type=customer_type
        )
        return self._repo.add(customer)

    def list_customers(self) -> list[Customer]:
        return self._repo.get_all()

    def get_customer(self, customer_id: int) -> Customer:
        return self._repo.get_by_id_or_raise(customer_id)
    
    def search_customers(self, keyword: str | None = None) -> list[Customer]:
        return self._repo.search(keyword=keyword)
    
    def update_customer(
        self,
        customer_id: int,
        full_name: str | None = None,
        email: str | None = None,
        phone: str | None = None,
    ) -> Customer:
        customer = self._repo.get_by_id_or_raise(customer_id)

        new_full_name = full_name if full_name is not None else customer.full_name
        new_email = email if email is not None else customer.email 
        new_phone = phone if phone is not None else customer.phone

        validated = Customer(
            id=customer.id,
            full_name=new_full_name,
            email=new_email,
            phone=new_phone,
            customer_type=customer.customer_type,
        )

        if new_email != customer.email and self._repo.get_by_email(new_email) is not None:
            raise InvalidCustomerDataError(f"Customer with email {new_email} already exists")
        
        customer.full_name = validated.full_name
        customer.email = validated.email
        customer.phone = validated.phone
        customer.updated_at = datetime.now()

        self._repo.update(customer)
        return customer
    
    def upgrade_to_vip(self, customer_id: int) -> Customer:
        customer = self._repo.get_by_id_or_raise(customer_id)
        customer.upgrade_to_vip()
        self._repo.update(customer)
        return customer

    def downgrade_to_regular(self, customer_id: int) -> Customer:
        customer = self._repo.get_by_id_or_raise(customer_id)
        customer.customer_type = CustomerType.REGULAR
        customer.updated_at = datetime.now()
        self._repo.update(customer)
        return customer
    
    def remove_customer(self, customer_id: int) -> None:
        self._repo.get_by_id_or_raise(customer_id)  

        if self._repo.has_orders(customer_id):
            raise InvalidCustomerDataError(
                f"Cannot delete customer with id {customer_id} because they have associated orders."
            )
        self._repo.delete(customer_id)