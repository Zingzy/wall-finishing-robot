"""
Main entry point for the Wall Finishing Robot API.

This module serves as the entry point for the application and handles server startup.
All application logic is contained in the src package.
"""

from src.app import app  # noqa: F401 - Required for uvicorn to find the app
from src.config.loader import get_settings

if __name__ == "__main__":
    import uvicorn
    import os

    # Load settings
    settings = get_settings()

    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)

    print(f"Starting {settings.api.title} v{settings.api.version}")
    print(f"Server will run on {settings.server.host}:{settings.server.port}")
    print(f"Environment: {settings.environment}")
    print(f"Debug mode: {settings.debug}")

    uvicorn.run(
        "main:app",
        host=settings.server.host,
        port=settings.server.port,
        reload=settings.server.reload,
        log_level=settings.server.log_level,
    )
