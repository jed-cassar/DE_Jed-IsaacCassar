"""
Configuration settings for the application
"""
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    mongodb_url: str = "your_mongo_connection_string"
    database_name: str = "event_management_db"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"  # Ignore extra fields from environment
    )


settings = Settings()

