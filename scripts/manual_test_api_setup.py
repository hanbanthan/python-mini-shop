"""
python3 -m scripts.manual_test_api_setup
"""

import sys

try:
    from fastapi.testclient import TestClient
except ImportError as exc:
    print("Please install 'fastapi' to run this script")
    sys.exit(0)

def main() -> None:
    from src.api.app import app

    client = TestClient(app)

    # 1. Health check - API can run, not depend on database
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    print("Health check passed")

    # 2.Swagger UI - check OpenAPI schema is generated
    docs_response = client.get("/docs")
    assert docs_response.status_code == 200
    assert "swagger" in docs_response.text.lower()
    print("Swagger UI check passed")

    # 3. OpenAPi schema generated from type hints and Pydantic schema
    openapi_response = client.get("/opoenapi.json")
    assert openapi_response.status_code == 200
    schema = openapi_response.json()
    assert schema["info"]["title"] == "Mini Store Management API"
    assert "/health" in schema["paths"]
    print("OpenAPI schema check passed")

    print("All API setup checks passed successfully")

if __name__ == "__main__":
    main()
    
