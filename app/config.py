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
# This must be called before Settings() is instantiated
# Environment variables take precedence over .env file values
load_dotenv()


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    This class defines all application configuration settings. Values are loaded
    from environment variables, .env file, or default values (in that order).
    
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
    mongodb_url: str = "your_mongo_connection_string"
    database_name: str = "event_management_db"
    
    model_config = SettingsConfigDict(
        env_file=".env",           # Load from .env file
        case_sensitive=False,      # Environment variable names are case-insensitive
        extra="ignore"             # Ignore extra fields from environment (prevents errors)
    )


# Global settings instance
# This is imported throughout the application to access configuration
settings = Settings()

