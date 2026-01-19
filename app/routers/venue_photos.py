"""
Venue photo upload and retrieval endpoints

This module handles uploading and retrieving photos for venues:
- Upload: POST /upload_venue_photo/{venue_id} - Uploads a photo for a venue
- Retrieve: GET /venue_photos/{venue_id} - Lists all photos for a venue (metadata)
- Retrieve: GET /venue_photo/file/{photo_id} - Retrieves photo file by photo ID

Files are stored in MongoDB 'venue_photos' collection as binary data with metadata.
Multiple photos can be stored per venue.
"""
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from datetime import datetime
from bson import ObjectId
from io import BytesIO
from app.database import ensure_database, validate_object_id

router = APIRouter(tags=["venue_photos"])


@router.post("/upload_venue_photo/{venue_id}", response_model=dict, status_code=201)
async def upload_venue_photo(venue_id: str, file: UploadFile = File(...)):
    """
    Upload a photo for a venue.
    
    This endpoint uploads a photo file for a specific venue. The photo is stored
    in the MongoDB 'venue_photos' collection as binary data along with metadata including
    the venue_id, filename, content_type, and upload timestamp.
    
    Multiple photos can be uploaded for the same venue, allowing venues to have
    photo galleries.
    
    File Storage Mechanism:
    - Photos are stored directly in MongoDB documents as binary data (BSON Binary type)
    - Each document contains: venue_id, filename, content_type, content (binary), uploaded_at
    - MongoDB document size limit is 16MB, suitable for most image files
    - Multiple photos per venue are supported (each stored as a separate document)
    
    Args:
        venue_id: String ID of the venue this photo belongs to
        file: UploadFile object containing the image file
        
    Returns:
        Dictionary with success message and the photo document ID
        
    Raises:
        HTTPException: 500 if database is not connected, 400 if file is invalid
    """
    db = await ensure_database()
    
    # Read file content into memory
    # Design Decision: Reading entire file into memory for MongoDB binary storage
    # For venue photos typically under 5MB, this approach is optimal for simplicity.
    # Multiple photos per venue are supported - each photo is stored as a separate
    # document, allowing venues to have photo galleries without document size concerns.
    content = await file.read()
    
    # Create photo document with binary content
    # Design Decision: Store photos directly in MongoDB as binary data (BSON Binary type)
    # Multiple photos per venue: Each photo is a separate document, allowing galleries.
    # This is more flexible than storing all photos in a single array, as it:
    # - Allows individual photo retrieval without loading the entire gallery
    # - Supports easy addition/removal of individual photos
    # - Avoids document size issues (each photo is its own document)
    # Trade-off: Simplicity vs. storage - for photos <16MB each, this works well
    photo_doc = {
        "venue_id": venue_id,
        "filename": file.filename,
        "content_type": file.content_type,  # Preserve MIME type for proper rendering
        "content": content,  # Stored as binary in MongoDB (BSON Binary type)
        "uploaded_at": datetime.utcnow()  # Track upload time for sorting/ordering
    }
    
    result = await db.venue_photos.insert_one(photo_doc)
    # Design Decision: Convert ObjectId to string for JSON serialization
    return {"message": "Venue photo uploaded", "id": str(result.inserted_id)}


@router.get("/venue_photos/{venue_id}", response_model=list)
async def get_venue_photos(venue_id: str):
    """
    Get all photos for a venue (metadata only).
    
    This endpoint retrieves metadata for all photos associated with a specific venue.
    It queries the 'venue_photos' collection and returns a list of photo metadata
    (excluding binary content) sorted by upload date (most recent first).
    
    Args:
        venue_id: String ID of the venue
        
    Returns:
        List of dictionaries with photo metadata (excluding binary content)
        
    Raises:
        HTTPException: 500 if database is not connected
    """
    db = await ensure_database()
    
    # Find all photos for this venue, sorted by most recent first
    # Design Decision: Exclude binary content ({"content": 0}) when listing photos
    # This endpoint returns metadata only to avoid transferring large amounts of binary
    # data when listing multiple photos. Each photo can be retrieved individually via
    # the file endpoint, which is more efficient for displaying galleries.
    # Design Decision: Sort by uploaded_at descending - newest photos appear first
    # This is a common UX pattern for photo galleries where recent additions are most relevant
    photos = await db.venue_photos.find(
        {"venue_id": venue_id},
        {"content": 0}  # Exclude binary content from results - metadata only
    ).sort("uploaded_at", -1).to_list(100)
    
    # Design Decision: Limit to 100 photos to prevent overwhelming clients
    # For venues with many photos, consider adding pagination in future versions
    # Convert ObjectIds to strings and format dates for JSON serialization
    for photo in photos:
        photo["_id"] = str(photo["_id"])
        if "uploaded_at" in photo:
            photo["uploaded_at"] = photo["uploaded_at"].isoformat()  # ISO format for consistency
    
    return photos


@router.get("/venue_photo/file/{photo_id}")
async def get_venue_photo_file(photo_id: str):
    """
    Retrieve venue photo file by photo ID.
    
    This endpoint retrieves the actual photo image file from the database. The file
    is streamed back to the client using FastAPI's StreamingResponse with the appropriate
    content-type header for proper browser rendering.
    
    File Retrieval Mechanism:
    - The binary content is retrieved from MongoDB
    - StreamingResponse is used to stream the file to the client
    - Content-Type header is set from stored metadata for proper browser handling
    - BytesIO is used to create a file-like object from the binary data
    - Content-Disposition header allows inline display or download
    
    Args:
        photo_id: String ID of the photo document
        
    Returns:
        StreamingResponse with the image file and proper headers
        
    Raises:
        HTTPException: 404 if photo not found, 400 if ID format is invalid
    """
    db = await ensure_database()
    
    try:
        # Design Decision: Validate ObjectId before database query
        obj_id = validate_object_id(photo_id)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid photo ID format: {photo_id}")
    
    # Retrieve photo document
    photo = await db.venue_photos.find_one({"_id": obj_id})
    
    if not photo:
        raise HTTPException(status_code=404, detail=f"Photo with ID {photo_id} not found")
    
    # Design Decision: Use BytesIO to create a file-like object from binary content
    # BytesIO allows StreamingResponse to handle binary data efficiently without
    # writing to disk, which is ideal for serverless environments
    file_content = BytesIO(photo["content"])
    
    # Design Decision: Use StreamingResponse with proper media_type and Content-Disposition
    # - media_type: Ensures browsers render images correctly (image/jpeg, image/png, etc.)
    # - Content-Disposition: "inline" allows browser to display directly in galleries;
    #   "attachment" would force download, which is less user-friendly for photos
    # - filename: Helps with caching, saving, and browser identification
    # StreamingResponse is more efficient than FileResponse when content is in memory,
    # making it suitable for serverless deployments where disk access is limited
    return StreamingResponse(
        file_content,
        media_type=photo.get("content_type", "image/jpeg"),  # Default to JPEG if not set
        headers={
            "Content-Disposition": f'inline; filename="{photo.get("filename", "photo")}"'
        }
    )

