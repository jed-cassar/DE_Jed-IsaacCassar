"""
Database connection and configuration
"""
import motor.motor_asyncio
from app.config import settings

# MongoDB client instance
client: motor.motor_asyncio.AsyncIOMotorClient = None
database = None


async def connect_to_mongo():
    """Create database connection"""
    global client, database
    client = motor.motor_asyncio.AsyncIOMotorClient(settings.mongodb_url)
    database = client[settings.database_name]
    print(f"Connected to MongoDB: {settings.database_name}")


async def close_mongo_connection():
    """Close database connection"""
    global client
    if client:
        client.close()
        print("Disconnected from MongoDB")


def get_database():
    """Get the database instance"""
    return database

