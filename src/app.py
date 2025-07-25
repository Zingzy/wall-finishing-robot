"""Main FastAPI application for wall finishing robot control system."""

import time
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Any

from fastapi import FastAPI, status, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from src.config.loader import get_settings
from src.config.schemas import Settings
from src.models.trajectory import create_db_and_tables
from src.api.v1.router import router as v1_router


def configure_logging(settings: Settings) -> None:
    """Configure Loguru logging based on settings."""
    # Remove default handler
    logger.remove()

    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(settings.logging.file_path)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)

    # Add file handler
    logger.add(
        settings.logging.file_path,
        rotation=settings.logging.rotation,
        retention=settings.logging.retention,
        level=settings.logging.level,
        format=settings.logging.format,
    )

    # Add console handler for development
    if settings.debug:
        logger.add(
            lambda msg: print(msg, end=""),
            level=settings.logging.level,
            format=settings.logging.format,
        )


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    # Load settings
    settings = get_settings()

    # Configure logging
    configure_logging(settings)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
        """Application lifespan manager to handle startup/shutdown events."""
        # Startup
        logger.info("Starting Wall Finishing Robot API")
        create_db_and_tables()
        yield
        # Shutdown
        logger.info("Shutting down Wall Finishing Robot API")

    # Create FastAPI application
    app = FastAPI(
        title=settings.api.title,
        description=settings.api.description,
        version=settings.api.version,
        docs_url=settings.api.docs_url,
        redoc_url=settings.api.redoc_url,
        lifespan=lifespan,
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors.allow_origins,
        allow_credentials=settings.cors.allow_credentials,
        allow_methods=settings.cors.allow_methods,
        allow_headers=settings.cors.allow_headers,
    )

    # Mount static files for frontend
    app.mount("/static", StaticFiles(directory="src/static"), name="static")

    # Exception handlers
    @app.exception_handler(ValueError)
    async def value_error_exception_handler(request: Request, exc: ValueError) -> JSONResponse:
        """Handle ValueError exceptions with proper logging."""
        logger.error(f"ValueError in {request.url.path}: {str(exc)}")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exc)})

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Handle general exceptions with proper logging."""
        logger.error(f"Unexpected error in {request.url.path}: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )

    # Root endpoint
    @app.get("/", summary="Root endpoint")
    async def root() -> dict[str, str]:
        """Root endpoint with basic API information."""
        return {
            "message": settings.api.title,
            "version": settings.api.version,
            "docs": settings.api.docs_url,
            "frontend": "/static/index.html",
        }

    # Health check endpoint
    @app.get("/health", summary="Health check")
    async def health_check() -> dict[str, Any]:
        """Health check endpoint."""
        return {"status": "healthy", "timestamp": time.time()}

    # Include API routers
    app.include_router(v1_router)

    return app


# Create the app instance
app = create_app()
