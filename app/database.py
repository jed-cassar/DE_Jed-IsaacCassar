"""
Database connection and configuration

This module manages the MongoDB database connection using Motor (async MongoDB driver).
It provides helper functions for common database operations like finding, updating,
and deleting documents by ID.

Database Connection Lifecycle:
- Connection is established on FastAPI startup event
- Connection is closed on FastAPI shutdown event
- Global variables store client and database instances for reuse

For serverless deployments (Vercel), connections may be handled differently
due to function lifecycle constraints.
"""
import motor.motor_asyncio
from bson import ObjectId
from bson.errors import InvalidId
from typing import Optional, Dict, Any
import certifi
from app.config import settings

# Global MongoDB client and database instances
# These are initialized on application startup and reused for all requests
client: motor.motor_asyncio.AsyncIOMotorClient = None
database = None


async def connect_to_mongo():
    """
    Create and initialize MongoDB database connection.
    
    This function is called during FastAPI startup event. It creates an async
    Motor client using the MongoDB connection string from environment variables
    and selects the database specified in configuration.
    
    Database Connection Process:
    1. Creates AsyncIOMotorClient with connection string from settings
    2. Selects database by name from settings
    3. Stores client and database in global variables for reuse
    4. Connection is reused across all requests for efficiency
    
    Connection String Formats:
    - Local MongoDB: "mongodb://localhost:27017"
    - MongoDB Atlas: "mongodb+srv://username:password@cluster.mongodb.net/"
      (mongodb+srv:// automatically handles SSL/TLS for Atlas)
    
    Raises:
        ConnectionError: If MongoDB connection string is invalid or unreachable
    """
    global client, database
    try:
        # For MongoDB Atlas, use mongodb+srv:// which automatically handles SSL/TLS
        # For local MongoDB, use mongodb://localhost:27017
        
        # Determine if this is an Atlas connection (mongodb+srv://)
        is_atlas = 'mongodb+srv://' in settings.mongodb_url
        
        # Configure connection parameters
        connection_params = {
            'serverSelectionTimeoutMS': 20000,  # 20 second timeout for connection attempts
            'connectTimeoutMS': 20000,  # 20 second timeout for initial connection
            'socketTimeoutMS': 20000,  # 20 second timeout for socket operations
        }
        
        # For Atlas connections, explicitly configure TLS with certifi certificates
        # This fixes TLSV1_ALERT_INTERNAL_ERROR on macOS
        if is_atlas:
            # Use certifi's certificate bundle for SSL verification
            # This is often needed on macOS to resolve SSL handshake issues
            connection_params['tlsCAFile'] = certifi.where()
            connection_params['tlsAllowInvalidCertificates'] = False
        
        client = motor.motor_asyncio.AsyncIOMotorClient(
            settings.mongodb_url,
            **connection_params
        )
        database = client[settings.database_name]
        
        # Test the connection by pinging the server
        await client.admin.command('ping')
        print(f"Connected to MongoDB: {settings.database_name}")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        print(f"Connection string format: {'mongodb+srv://' if 'mongodb+srv://' in settings.mongodb_url else 'mongodb://'}")
        print("For MongoDB Atlas, ensure you're using: mongodb+srv://username:password@cluster.mongodb.net/")
        print("For local MongoDB, ensure MongoDB is running and use: mongodb://localhost:27017")
        print("\nTroubleshooting tips:")
        print("1. Verify your connection string is correct")
        print("2. Check that your IP address is whitelisted in MongoDB Atlas")
        print("3. Ensure your username and password are URL-encoded if they contain special characters")
        print("4. Try updating your Python SSL certificates: pip install --upgrade certifi")
        print("5. On macOS, ensure certifi is installed: pip install certifi")
        raise


async def close_mongo_connection():
    """
    Close MongoDB database connection.
    
    This function is called during FastAPI shutdown event. It properly closes
    the MongoDB client connection and releases resources.
    
    Database Cleanup Process:
    1. Checks if client exists (may not exist if startup failed)
    2. Closes client connection
    3. Releases network resources
    """
    global client
    if client:
        client.close()
        print("Disconnected from MongoDB")


def get_database():
    """
    Get the MongoDB database instance.
    
    Returns the global database instance that was initialized during startup.
    This function is used throughout the application to access the database
    for performing operations on collections.
    
    Returns:
        Database instance (Motor AsyncIOMotorDatabase) or None if not connected
        
    Note:
        Returns None if database connection hasn't been established yet.
        Callers should check for None and handle appropriately.
    """
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
    Find a document by ID in the specified MongoDB collection.
    
    This is a generic helper function used by all endpoints that need to
    retrieve a single document by its ID. It handles ID validation and
    ObjectId conversion automatically.
    
    Database Operation:
    - Queries collection using MongoDB's find_one() with _id filter
    - Converts MongoDB ObjectId to string for JSON serialization
    - Returns None if document not found or ID is invalid
    
    Args:
        collection_name: Name of the MongoDB collection (e.g., "events", "venues")
        item_id: String representation of the document's MongoDB ObjectId
        
    Returns:
        Document dictionary with _id as string if found, None otherwise
        
    Example:
        event = await find_by_id("events", "507f1f77bcf86cd799439012")
        # Returns: {"_id": "507f1f77bcf86cd799439012", "name": "Event Name", ...}
    """
    db = get_database()
    if db is None:
        return None
    
    try:
        # Validate and convert string ID to MongoDB ObjectId
        obj_id = validate_object_id(item_id)
        
        # Get collection and query by _id
        collection = db[collection_name]
        document = await collection.find_one({"_id": obj_id})
        
        # Convert ObjectId to string for JSON serialization
        if document:
            document["_id"] = str(document["_id"])
        return document
    except ValueError:
        # Invalid ID format
        return None


async def update_by_id(collection_name: str, item_id: str, update_data: Dict[str, Any]) -> bool:
    """
    Update a document by ID in the specified MongoDB collection.
    
    This function performs a partial update using MongoDB's $set operator.
    Only the fields provided in update_data will be updated; other fields
    remain unchanged. None values are automatically filtered out.
    
    Database Operation:
    - Uses MongoDB's update_one() with $set operator for partial updates
    - Filters out None values to avoid overwriting fields with None
    - Returns True if document was modified, False if no changes made
    
    Args:
        collection_name: Name of the MongoDB collection (e.g., "events", "venues")
        item_id: String representation of the document's MongoDB ObjectId
        update_data: Dictionary of fields to update (e.g., {"name": "New Name", "max_attendees": 1000})
                    Fields with None values are automatically excluded
        
    Returns:
        True if document was successfully updated, False otherwise
        (False can mean: document not found, invalid ID, or no valid fields to update)
        
    Example:
        updated = await update_by_id("events", "507f1f77bcf86cd799439012", {"max_attendees": 1200})
        # Updates only the max_attendees field, leaves other fields unchanged
    """
    db = get_database()
    if db is None:
        return False
    
    try:
        # Validate and convert string ID to MongoDB ObjectId
        obj_id = validate_object_id(item_id)
        
        # Remove None values from update_data to avoid overwriting fields
        # This allows partial updates where only specified fields are changed
        filtered_update = {k: v for k, v in update_data.items() if v is not None}
        
        # If no valid fields to update, return False
        if not filtered_update:
            return False
        
        # Perform update using $set operator (partial update)
        collection = db[collection_name]
        result = await collection.update_one(
            {"_id": obj_id},
            {"$set": filtered_update}
        )
        
        # Return True if document was modified
        return result.modified_count > 0
    except ValueError:
        # Invalid ID format
        return False


async def delete_by_id(collection_name: str, item_id: str) -> bool:
    """
    Delete a document by ID from the specified MongoDB collection.
    
    This function permanently removes a document from the database.
    The deletion is atomic and cannot be undone.
    
    Database Operation:
    - Uses MongoDB's delete_one() to remove document by _id
    - Returns True if document was deleted, False if not found or invalid ID
    
    Args:
        collection_name: Name of the MongoDB collection (e.g., "events", "venues")
        item_id: String representation of the document's MongoDB ObjectId
        
    Returns:
        True if document was successfully deleted, False otherwise
        (False can mean: document not found or invalid ID format)
        
    Example:
        deleted = await delete_by_id("events", "507f1f77bcf86cd799439012")
        # Returns True if event was deleted, False if not found
        
    Warning:
        This operation is permanent. Consider implementing soft deletes
        (marking as deleted) if you need to recover deleted data.
    """
    db = get_database()
    if db is None:
        return False
    
    try:
        # Validate and convert string ID to MongoDB ObjectId
        obj_id = validate_object_id(item_id)
        
        # Perform deletion
        collection = db[collection_name]
        result = await collection.delete_one({"_id": obj_id})
        
        # Return True if document was deleted
        return result.deleted_count > 0
    except ValueError:
        # Invalid ID format
        return False

