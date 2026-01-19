"""
Configuration settings for the application

This module handles application configuration using Pydantic Settings, which provides
type-safe configuration management with automatic environment variable loading.

Configuration Sources (in order of precedence):
1. Environment variables (highest priority)
2. .env file in project root
3. Default values defined in Settings class (lowest priority)

The Settings class uses Pydantic for validation, ensuring type safety and proper
error messages if required configuration is missing or invalid.
"""
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load environment variables from .env file
# Design Decision: Load .env file before Settings() instantiation
# This allows .env file values to be available as fallback when environment
# variables are not set. load_dotenv() reads .env from project root.
# Design Decision: Environment variables take precedence over .env file values
# This allows overriding .env file settings in different deployment environments
# (development, staging, production) without changing code or .env files
load_dotenv()


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    This class defines all application configuration settings. Values are loaded
    from environment variables, .env file, or default values (in that order).
    
    Design Decision: Using Pydantic Settings (BaseSettings) provides:
    - Type safety: Settings are validated at runtime with proper types
    - Automatic validation: Invalid values raise clear error messages
    - Multiple sources: Environment variables, .env file, or default values
    - Precedence order: Environment variables > .env file > default values
    
    Attributes:
        mongodb_url: MongoDB connection string
            - Format: "mongodb://localhost:27017" (local) or 
                      "mongodb+srv://user:pass@cluster.mongodb.net/" (Atlas)
            - Can be set via MONGODB_URL environment variable
            - Default: "your_mongo_connection_string" (must be changed)
        
        database_name: Name of the MongoDB database to use
            - Can be set via DATABASE_NAME environment variable
            - Default: "event_management_db"
    
    Example:
        # Set via environment variable
        export MONGODB_URL="mongodb://localhost:27017"
        export DATABASE_NAME="my_database"
        
        # Or create .env file:
        # MONGODB_URL=mongodb://localhost:27017
        # DATABASE_NAME=my_database
    """
    # Design Decision: Default values provide fallback when environment variables are not set
    # This allows the app to run with sensible defaults during development
    # In production, these should be overridden via environment variables for security
    mongodb_url: str = "your_mongo_connection_string"
    database_name: str = "event_management_db"
    
    # Design Decision: model_config uses SettingsConfigDict for configuration
    # This replaces deprecated Config class in Pydantic v2
    model_config = SettingsConfigDict(
        env_file=".env",           # Load from .env file as fallback
        # Design Decision: case_sensitive=False makes environment variable names case-insensitive
        # This provides flexibility - MONGODB_URL, mongodb_url, or MongoDB_Url all work
        # This is important because different systems have different conventions
        case_sensitive=False,      # Environment variable names are case-insensitive
        # Design Decision: extra="ignore" prevents errors from extra environment variables
        # In cloud deployments (Vercel, AWS, etc.), many environment variables may be set
        # that aren't part of our Settings class. Ignoring them prevents validation errors
        extra="ignore"             # Ignore extra fields from environment (prevents errors)
    )


# Global settings instance
# Design Decision: Create a singleton Settings instance at module level
# This ensures configuration is loaded once when the module is imported and
# provides consistent settings across the entire application.
# Design Decision: Using a global instance instead of passing Settings around
# - Simplifies imports: Any module can access settings via `from app.config import settings`
# - Single source of truth: Configuration is loaded and validated once
# - Performance: Settings are parsed and validated at startup, not per-request
# Trade-off: Global state can make testing harder, but Pydantic allows easy override
# In tests, Settings can be mocked or environment variables can be temporarily set
settings = Settings()

