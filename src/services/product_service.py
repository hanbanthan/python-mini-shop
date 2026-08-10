from decimal import Decimal

from src.exceptions import InvalidProductDataError
from src.models.product import Product
from src.repositories.product_repository import ProductRepository

class ProductService:
    def __init__(self, product_repository: ProductRepository | None = None) -> None:
        # Constructor injection allow pass fake/mock repository when unit test
        self._repo = product_repository or ProductRepository()

    def add_product(
        self,
        name: str,
        category: str,
        price: Decimal,
        stock_quantity: int = 0,
        tags: set[str] | None = None,
    ) -> Product:
        self._validate_stock_quantity(stock_quantity)

        if price <= 0:
            raise InvalidProductDataError("Price must be greater than 0")

        product = Product(
            id=None, 
            name=name, 
            category=category, 
            price=price, tags=tags or set()
        )
        if stock_quantity > 0:
            product.increase_stock(stock_quantity)
        return self._repo.add(product)

    def list_products(self) -> list[Product]:
        return self._repo.get_all()

    def get_product(self, product_id: int) -> Product:
        return self._repo.get_by_id_or_raise(product_id)
    
    def search_products (
        self,
        keyword: str | None = None,
        category: str | None = None,
        min_price: Decimal | None = None,
        max_price: Decimal | None = None,
        tag: str | None = None,
        active_only: bool = False,
    ) -> list[Product]:
        products = self._repo.search(keyword=keyword, category=category, active_only=active_only)

        if min_price is not None:
            products = [p for p in products if p.price >= min_price]
        if max_price is not None:
            products = [p for p in products if p.price <= max_price]
        if tag is not None:
            tag_lower = tag.lower()
            products = [p for p in products if tag_lower in {t.lower() for t in p.tags}]
        
        return products
    
    def update_product(
        self,
        product_id: int,
        name: str | None = None,
        category: str | None = None,
        price: Decimal | None = None,
        stock_quantity: int | None = None,
        tags: set[str] | None = None,
    ) -> Product:
        product = self._repo.get_by_id_or_raise(product_id)

        new_name = name if name is not None else product.name
        new_category = category if category is not None else product.category
        new_price = price if price is not None else product.price

        if not new_name or not new_name.strip():
            raise InvalidProductDataError("Product name can not be empty")
        if new_price < 0:
            raise InvalidProductDataError("Product price can not be negative")
        
        product.name = new_name
        product.category = new_category
        product.price = new_price

        if tags is not None:
            product.tags = tags
        
        if stock_quantity is not None:
            self._validate_stock_quantity(stock_quantity)
            diff = stock_quantity - product.stock_quantity
            if diff > 0:
                product.increase_stock(diff)
            elif diff < 0:
                product.reduce_stock(-diff)
        self._repo.update(product)
        return product

    def remove_product(self, product_id: int) -> None:
        self._repo.get_by_id_or_raise(product_id) 
        
        if self._repo.has_been_sold(product_id):
            self._repo.deactivate(product_id)
        else:
            self._repo.delete_hard(product_id)

    @staticmethod
    def _validate_stock_quantity(stock_quantity: int) -> None:
        if not isinstance(stock_quantity, int) or isinstance(stock_quantity, bool):
            raise InvalidProductDataError("Stock quantity must be an integer")
        if stock_quantity < 0:
            raise InvalidProductDataError("Stock quantity can not be negative")

