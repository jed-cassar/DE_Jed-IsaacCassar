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
# Design Decision: Using global variables allows connection reuse across all requests,
# which is more efficient than creating new connections for each request.
# Trade-off: This approach works well for traditional deployments, but in serverless
# environments (like Vercel), connections may be reset between invocations.
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
        # Design Decision: Different connection handling for Atlas vs local MongoDB
        # Atlas uses mongodb+srv:// which automatically handles DNS resolution and SSL/TLS
        is_atlas = 'mongodb+srv://' in settings.mongodb_url
        
        # Configure connection parameters optimized for serverless environments
        # Design Rationale: These timeouts and pool sizes are chosen to balance
        # performance and reliability in serverless environments like Vercel:
        # - Longer timeouts (30s) account for cold starts and network latency
        # - Smaller pool size (10) prevents connection exhaustion in serverless
        # - minPoolSize=1 keeps at least one connection ready for faster responses
        connection_params = {
            'serverSelectionTimeoutMS': 30000,  # 30 second timeout for connection attempts
            # Design Decision: 30s allows time for serverless function initialization
            # and network establishment, especially important for cold starts
            'connectTimeoutMS': 30000,  # 30 second timeout for initial connection
            'socketTimeoutMS': 30000,  # 30 second timeout for socket operations
            # Design Decision: maxPoolSize=10 is a balance between performance and
            # resource usage. Too large wastes connections; too small causes queuing.
            # In serverless, we use a smaller pool since functions may scale horizontally
            'maxPoolSize': 10,  # Connection pool size
            'minPoolSize': 1,  # Minimum connections - keeps one ready for faster response
        }
        
        # For Atlas connections, let MongoDB handle SSL automatically
        # Design Decision: Not setting tlsCAFile explicitly in serverless environments
        # because Vercel and similar platforms have their own certificate management.
        # The system's default certificate store works better than trying to bundle
        # certificates in the deployment.
        if is_atlas:
            # Enable TLS explicitly (mongodb+srv:// does this, but being explicit)
            # Design Decision: Explicitly setting TLS parameters provides clarity
            # and ensures security even if connection string parsing changes
            connection_params['tls'] = True
            connection_params['tlsAllowInvalidCertificates'] = False
            # Design Decision: Don't set tlsCAFile - let the system use default certificates
            # This avoids certificate bundle management in serverless environments like Vercel
            # where the runtime environment manages certificates differently
        
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
        print("1. Verify your connection string is correct in Vercel environment variables")
        print("2. Check MongoDB Atlas Network Access - allow connections from 0.0.0.0/0 (or Vercel's IPs)")
        print("3. Ensure your username and password are URL-encoded if they contain special characters")
        print("4. Verify MONGODB_URL and DATABASE_NAME are set correctly in Vercel dashboard")
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


async def ensure_database():
    """
    Ensure database connection is established.
    
    For serverless environments (like Vercel), startup events may not run reliably.
    This function ensures the database connection is established on first use.
    
    This is safe to call multiple times - it will only connect once.
    """
    global client, database
    # Design Decision: Lazy connection pattern for serverless environments
    # In serverless (Vercel), lifespan events may not execute reliably, so we
    # use this pattern to ensure connection on first request. The check for None
    # ensures we only connect once even if ensure_database() is called multiple times.
    if database is None:
        await connect_to_mongo()
    return database


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
        For serverless environments, use ensure_database() instead to lazily connect.
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
    # Design Decision: Centralized ObjectId validation prevents code duplication
    # and ensures consistent error handling across all endpoints. This function
    # validates that IDs are properly formatted MongoDB ObjectIds (24 hex chars)
    # before attempting database operations, providing better error messages.
    try:
        return ObjectId(id_string)
    except (InvalidId, TypeError):
        # Design Decision: Convert MongoDB-specific exceptions to ValueError for
        # consistency with Python conventions and easier error handling in routers
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
    # Design Decision: Use ensure_database() instead of get_database() to support
    # serverless environments where startup events may not run. This ensures
    # connection is established on first use.
    db = await ensure_database()
    
    try:
        # Validate and convert string ID to MongoDB ObjectId
        # Design Rationale: Validate early to provide clear error messages before
        # attempting database query, which improves developer experience
        obj_id = validate_object_id(item_id)
        
        # Get collection and query by _id
        collection = db[collection_name]
        document = await collection.find_one({"_id": obj_id})
        
        # Design Decision: Convert ObjectId to string for JSON serialization
        # MongoDB ObjectIds are not JSON-serializable, so we convert to string.
        # This is done in the database layer to keep serialization logic centralized
        # and consistent across all endpoints.
        if document:
            document["_id"] = str(document["_id"])
        return document
    except ValueError:
        # Invalid ID format - return None instead of raising to allow endpoints
        # to handle the error appropriately (e.g., return 404 vs 400)
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
    db = await ensure_database()
    
    try:
        # Validate and convert string ID to MongoDB ObjectId
        obj_id = validate_object_id(item_id)
        
        # Design Decision: Remove None values to avoid overwriting fields with None
        # This allows partial updates where clients only send fields they want to change.
        # Without filtering, None values would clear existing fields unintentionally.
        filtered_update = {k: v for k, v in update_data.items() if v is not None}
        
        # Design Decision: Return False if no valid fields to update rather than raising
        # This allows callers to distinguish between "no changes needed" and "not found"
        if not filtered_update:
            return False
        
        # Design Decision: Use $set operator for partial updates
        # MongoDB's $set operator updates only specified fields, leaving others unchanged.
        # This is more efficient than replacing the entire document and preserves
        # fields that weren't included in the update request.
        collection = db[collection_name]
        result = await collection.update_one(
            {"_id": obj_id},
            {"$set": filtered_update}
        )
        
        # Design Decision: Check modified_count instead of matched_count
        # modified_count tells us if the document was actually changed (not just found).
        # This handles cases where the update values are the same as existing values.
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
    db = await ensure_database()
    
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

