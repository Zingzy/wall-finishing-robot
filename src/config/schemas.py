"""Configuration schemas for the wall finishing robot application."""

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseConfig(BaseModel):
    """Database configuration settings."""

    url: str = Field(default="sqlite:///./trajectories.db", description="Database URL")
    echo: bool = Field(default=False, description="Enable SQLAlchemy echo logging")


class LoggingConfig(BaseModel):
    """Logging configuration settings."""

    level: str = Field(default="INFO", description="Log level")
    file_path: str = Field(default="logs/app.log", description="Log file path")
    rotation: str = Field(default="10 MB", description="Log rotation size")
    retention: str = Field(default="1 week", description="Log retention period")
    format: str = Field(
        default="{time:YYYY-MM-DD HH:mm:ss} | {level} | {module}:{function}:{line} | {message}",
        description="Log format string",
    )


class ServerConfig(BaseModel):
    """Server configuration settings."""

    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    reload: bool = Field(default=True, description="Enable auto-reload in development")
    log_level: str = Field(default="info", description="Uvicorn log level")


class CORSConfig(BaseModel):
    """CORS configuration settings."""

    allow_origins: list[str] = Field(default=["*"], description="Allowed origins")
    allow_credentials: bool = Field(default=True, description="Allow credentials")
    allow_methods: list[str] = Field(default=["*"], description="Allowed methods")
    allow_headers: list[str] = Field(default=["*"], description="Allowed headers")


class APIConfig(BaseModel):
    """API configuration settings."""

    title: str = Field(default="Wall Finishing Robot API", description="API title")
    description: str = Field(
        default="API for autonomous wall-finishing robot trajectory generation and management",
        description="API description",
    )
    version: str = Field(default="1.0.0", description="API version")
    docs_url: str = Field(default="/docs", description="OpenAPI docs URL")
    redoc_url: str = Field(default="/redoc", description="ReDoc URL")


class Settings(BaseSettings):
    """Main application settings."""

    # Environment
    environment: str = Field(default="development", description="Environment name")
    debug: bool = Field(default=False, description="Debug mode")
    secret_key: str = Field(..., description="Secret key for the application")

    # Component configurations
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    server: ServerConfig = Field(default_factory=ServerConfig)
    cors: CORSConfig = Field(default_factory=CORSConfig)
    api: APIConfig = Field(default_factory=APIConfig)

    model_config = SettingsConfigDict(
        env_file=".env", env_nested_delimiter="__", case_sensitive=False
    )
