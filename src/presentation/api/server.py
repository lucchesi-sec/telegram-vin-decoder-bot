"""Main API server following DDD principles with proper separation of concerns."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from src.presentation.api.routes.vehicle_routes import router as vehicle_router
from src.presentation.api.routes.user_routes import router as user_router
from src.presentation.api.routes.health_routes import router as health_router
from src.presentation.api.routes.auth_routes import router as auth_router
from src.presentation.api.middleware.cors import add_cors_middleware
from src.presentation.api.middleware.error_handling import add_exception_handlers


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="VIN Decoder API",
        description="Domain-driven VIN decoder service",
        version="2.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Add middleware
    add_cors_middleware(app)
    add_exception_handlers(app)
    
    # Add routes
    app.include_router(health_router)
    app.include_router(auth_router)
    app.include_router(vehicle_router)
    app.include_router(user_router)
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info("VIN Decoder API server initialized")
    
    return app


# Create the app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)