"""
Database connection and configuration
"""
import motor.motor_asyncio
from bson import ObjectId
from bson.errors import InvalidId
from typing import Optional, Dict, Any
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


def validate_object_id(id_string: str) -> ObjectId:
    """
    Validate and convert string ID to ObjectId.
    
    Args:
        id_string: String representation of MongoDB ObjectId
        
    Returns:
        ObjectId instance
        
    Raises:
        ValueError: If the ID string is invalid
    """
    try:
        return ObjectId(id_string)
    except (InvalidId, TypeError):
        raise ValueError(f"Invalid ID format: {id_string}")


async def find_by_id(collection_name: str, item_id: str) -> Optional[Dict[str, Any]]:
    """
    Find a document by ID in the specified collection.
    
    Args:
        collection_name: Name of the MongoDB collection
        item_id: String ID of the document to find
        
    Returns:
        Document dictionary if found, None otherwise
    """
    db = get_database()
    if not db:
        return None
    
    try:
        obj_id = validate_object_id(item_id)
        collection = db[collection_name]
        document = await collection.find_one({"_id": obj_id})
        if document:
            document["_id"] = str(document["_id"])
        return document
    except ValueError:
        return None


async def update_by_id(collection_name: str, item_id: str, update_data: Dict[str, Any]) -> bool:
    """
    Update a document by ID in the specified collection.
    
    Args:
        collection_name: Name of the MongoDB collection
        item_id: String ID of the document to update
        update_data: Dictionary of fields to update (exclude None values)
        
    Returns:
        True if document was updated, False otherwise
    """
    db = get_database()
    if not db:
        return False
    
    try:
        obj_id = validate_object_id(item_id)
        # Remove None values from update_data
        filtered_update = {k: v for k, v in update_data.items() if v is not None}
        
        if not filtered_update:
            return False
        
        collection = db[collection_name]
        result = await collection.update_one(
            {"_id": obj_id},
            {"$set": filtered_update}
        )
        return result.modified_count > 0
    except ValueError:
        return False


async def delete_by_id(collection_name: str, item_id: str) -> bool:
    """
    Delete a document by ID from the specified collection.
    
    Args:
        collection_name: Name of the MongoDB collection
        item_id: String ID of the document to delete
        
    Returns:
        True if document was deleted, False otherwise
    """
    db = get_database()
    if not db:
        return False
    
    try:
        obj_id = validate_object_id(item_id)
        collection = db[collection_name]
        result = await collection.delete_one({"_id": obj_id})
        return result.deleted_count > 0
    except ValueError:
        return False

