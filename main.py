from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Settings
class Settings(BaseSettings):
    mongodb_url: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    database_name: str = os.getenv("DATABASE_NAME", "mydatabase")
    
    class Config:
        env_file = ".env"

settings = Settings()

# FastAPI app
app = FastAPI(title="Database Essentials API", version="1.0.0")

# MongoDB client
client = None
database = None

@app.on_event("startup")
async def startup_db_client():
    global client, database
    client = AsyncIOMotorClient(settings.mongodb_url)
    database = client[settings.database_name]
    print(f"Connected to MongoDB: {settings.database_name}")

@app.on_event("shutdown")
async def shutdown_db_client():
    global client
    if client:
        client.close()
        print("Disconnected from MongoDB")

@app.get("/")
async def root():
    return {"message": "Welcome to Database Essentials API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": settings.database_name}

