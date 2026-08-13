
from decimal import Decimal

from src.models.enums import CustomerType
from src.repositories.product_repository import ProductRepository

def _create_product(app_client, **overides):
    payload = {
        "name": "Test Product",
        "category": "Test Category",
        "price": "9.99",
        "stock_quantity": 100,
        "tags": ["test", "product"],
    }
    payload.update(overides)
    response = app_client.post("/products", json=payload)
    assert response.status_code == 201
    return response.json()

def _create_customer(app_client, **overides):
    payload = {
        "full_name": "Test Customer",
        "email": "test@example.com",
        "phone": "1234567890",
        "customer_type": CustomerType.REGULAR.value,
    }
    payload.update(overides)
    response = app_client.post("/customers", json=payload)
    assert response.status_code == 201
    return response.json()

def test_create_product_success_returns_201(api_client):
    response = api_client.post(
    "/products",
        json={
            "name": "Test Product",
            "category": "Test Category",
            "price": "9.99",
            "stock_quantity": 100,
            "tags": ["test", "product"],
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Test Product"
    assert body["category"] == "Test Category"
    assert Decimal(body["price"]) == Decimal("9.99")
    assert body["stock_quantity"] == 100
    assert set(body["tags"]) == {"test", "product"}
    assert body["is_active"] is True

def test_create_product_invalid_data_returns_400(api_client):
    response = api_client.post(
        "/products",
        json={
            "name": "",
            "category": "Electronics",
            "price": "100000.00",
            "stock_quantity": 1,
            "tags": [],
        },
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid product data: name must not be empty."}

def test_get_product_not_found_returns_404(api_client):
    response = api_client.get("/products/999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_create_customer_success_returns_201(api_client):
    response = api_client.post(
        "/customers",
        json={
            "full_name": "Test Customer",
            "email": "test@example.com",
            "phone": "1234567890",
            "customer_type": CustomerType.REGULAR.value,
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["full_name"] == "Test Customer"
    assert body["email"] == "test@example.com"
    assert body["phone"] == "1234567890"
    assert body["customer_type"] == CustomerType.REGULAR.value

def test_create_customer_invalid_data_returns_400(api_client):
    response = api_client.post(
        "/customers",
        json={
            "full_name": "",
            "email": "invalid-email",
            "phone": "1234567890",
            "customer_type": CustomerType.REGULAR.value,
        },
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid customer data: full_name must not be empty."}

def test_get_customer_not_found_returns_404(api_client):
    response = api_client.get("/customers/999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_create_order_success_returns_201(api_client):
    product = _create_product(api_client)
    customer = _create_customer(api_client)

    response = api_client.post(
        "/orders",
        json={
            "customer_id": customer["id"],
            "items": [
                {"product_id": product["id"], "quantity": 2}
            ],
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["customer_id"] == customer["id"]
    assert len(body["items"]) == 1
    assert body["items"][0]["product_id"] == product["id"]
    assert body["items"][0]["quantity"] == 2