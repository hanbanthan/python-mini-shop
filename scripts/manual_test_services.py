
from decimal import Decimal

from src.services.product_service import ProductService
from src.exceptions import InvalidProductDataError, ProductNotFoundError

def test_product_service():
    print("\n=== ProductService ====")
    service = ProductService()

    # 1. Add a correct product
    product = service.add_product(
        name="Test Product",
        category="Test Category",
        price=Decimal("1500000"),
        stock_quantity=10,
        tags={"test", "product"}
    )
    print("Added product:", product.id, product.name, product.price, product.stock_quantity)

    # 2. Add a incorrect product
    try:
        service.add_product(
            name="",
            category="Test Category",
            price=Decimal("100"),
            stock_quantity=1,
        )
        raise AssertionError("it should raise InvalidProductDataError (empty name)")
    except InvalidProductDataError:
        print("Correctly raised InvalidProductDataError for empty name")
    
    try:
        service.add_product(
            name="Test",
            category="Test Category",
            price=Decimal("-100"),
            stock_quantity=1,
        )
        raise AssertionError("it should raise InvalidProductDataError (negative price)")
    except InvalidProductDataError:
        print("Correctly raised InvalidProductDataError for negative price")
    
    try:
        service.add_product(
            name="Test",
            category="Test Category",
            price=Decimal("100"),
            stock_quantity=-5,
        )
        raise AssertionError("It should raise InvalidProductDataError (negative stock qunantity)")
    except InvalidProductDataError:
        print("Correctly raised InvalidProductDataError for negative stock quantity")
    
    # 3. Find product existing
    found = service.get_product(product.id)
    assert found.name == product.name
    print("get_product_by_id passed:", found.name)

    # 4. Find product not existing
    try:
        service.get_product(9999)
        raise AssertionError("Expected ProductNotFoundError for non-existent product")  
    except ProductNotFoundError:
        print("get_product_by_id correctly raised ProductNotFoundError for non-existent product")   
    
    # 5. Search according to keyword + tag + price range
    results = service.search_products(keyword="Test", tag="product", min_price=Decimal("1000000"))
    assert any(p.id == product.id for p in results)
    print("search_products passed, found", len(results), "results")

    results_out_of_range = service.search_products(keyword="Test", tag="product", min_price=Decimal("2000000"))
    assert not any(p.id == product.id for p in results_out_of_range)
    print("search_products with min_price out of range passed, found", len(results_out_of_range), "results")

    # 6. Update product
    updated = service.update_product(product.id, price=Decimal("1400000"))
    assert updated.price == Decimal("1400000")
    assert updated.name == product.name
    print("update_product passed new price, name unchanged :", updated.price, updated.name)

    # 7. Update product with correct stock quantity
    updated = service.update_product(product.id, stock_quantity=20)
    assert updated.stock_quantity == 20
    print("update_product passed new stock quantity:", updated.stock_quantity)

    # 8. Update product with incorrect stock quantity
    try:
        service.update_product(product.id, stock_quantity=-5)
        raise AssertionError("Expected InvalidProductDataError for negative stock quantity")
    except InvalidProductDataError:
        print("update_product correctly raised InvalidProductDataError for negative stock quantity")
    
    # 9. Update product not existing
    try:
        service.update_product(9999, price=Decimal("100"))
        raise AsssertionError("Expected ProductNotFoundError for non-existent product")
    except ProductNotFoundError:
        print("update_product correctly raised ProductNotFoundError for non-existent product")

    # 10. Delete never sold product -> hard delete
    never_sold = service.add_product(
        name="Never Sold Product",
        category="Test Category",
        price=Decimal("1000000"),
        stock_quantity=5,
    )
    service.remove_product(never_sold.id)
    try:
        service.get_product(never_sold.id)
        raise AssertionError("Expected ProductNotFoundError for deleted product")
    except ProductNotFoundError:
        print("remove_product correctly hard deleted never sold product")
    
def main() -> None:
    product_id = test_product_service()
    print("All service tests passed successfully.")

if __name__ == "__main__":
    main()