"""FastAPI application factory

CLI(`main.py`) and API (`run through `uvicorn src.api.app:app`) using same
Service/Repository/Database layer 

Run: uvicorn src.api.app:app --reload
Swagger UI: http://localhost:8000/docs
OpenAPI schema: http://localhost:8000/openapi.json
"""

from fastapi import FastAPI

from src.api.exception_handlers import register_exception_handlers
from src.api.routers import router as api_router
from src.config.logging_config import configure_logging
from src.database.init_db import init_db

def create_app() -> FastAPI:
    """Application factory - seperate from `app` module level
    to test easy (each test can call 'create_app()' with different config
    instead of using 1 global app instance)
    """
    configure_logging()
    init_db() #idempotent - auto apply migrations, safe to call multiple times

    app = FastAPI(
        title="Mini Store Management API",
        description=(
            "REST API for managing a mini store"
        ),
        version="1.0.0",
    )

    register_exception_handlers(app)
    app.include_router(api_router)

    @app.get("/health", tags=["health"])
    def health_check() -> dict:
        """ Check API is running - use for load balancer/monitoring, 
        not depend on database
        """
        return {"status": "ok"}
    
    return app

app = create_app()