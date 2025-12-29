"""
Event poster upload and retrieval endpoints

This module handles uploading and retrieving event poster images:
- Upload: POST /upload_event_poster/{event_id} - Uploads a poster image for an event
- Retrieve: GET /event_poster/{event_id} - Retrieves poster metadata by event ID
- Retrieve: GET /event_poster/file/{poster_id} - Retrieves poster file by poster ID

Files are stored in MongoDB 'event_posters' collection as binary data with metadata.
"""
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from datetime import datetime
from bson import ObjectId
from bson.errors import InvalidId
from io import BytesIO
from app.database import get_database, validate_object_id

router = APIRouter(tags=["posters"])


@router.post("/upload_event_poster/{event_id}", response_model=dict, status_code=201)
async def upload_event_poster(event_id: str, file: UploadFile = File(...)):
    """
    Upload an event poster image.
    
    This endpoint uploads a poster image file for a specific event. The file is stored
    in the MongoDB 'event_posters' collection as binary data along with metadata including
    the event_id, filename, content_type, and upload timestamp.
    
    File Storage Mechanism:
    - Files are stored directly in MongoDB documents as binary data (BSON Binary type)
    - Each document contains: event_id, filename, content_type, content (binary), uploaded_at
    - MongoDB document size limit is 16MB, suitable for most image files
    
    Args:
        event_id: String ID of the event this poster belongs to
        file: UploadFile object containing the image file
        
    Returns:
        Dictionary with success message and the poster document ID
        
    Raises:
        HTTPException: 500 if database is not connected, 400 if file is invalid
    """
    db = get_database()
    if db is None:
        raise HTTPException(status_code=500, detail="Database not connected")
    
    # Read file content
    content = await file.read()
    
    # Create poster document with binary content
    poster_doc = {
        "event_id": event_id,
        "filename": file.filename,
        "content_type": file.content_type,
        "content": content,  # Stored as binary in MongoDB
        "uploaded_at": datetime.utcnow()
    }
    
    result = await db.event_posters.insert_one(poster_doc)
    return {"message": "Event poster uploaded", "id": str(result.inserted_id)}


@router.get("/event_poster/{event_id}", response_model=dict)
async def get_event_poster_metadata(event_id: str):
    """
    Get event poster metadata by event ID.
    
    This endpoint retrieves the poster metadata (not the file itself) for a specific event.
    It queries the 'event_posters' collection to find the most recent poster for the event.
    
    Args:
        event_id: String ID of the event
        
    Returns:
        Dictionary with poster metadata (excluding binary content)
        
    Raises:
        HTTPException: 404 if no poster found for the event
    """
    db = get_database()
    if db is None:
        raise HTTPException(status_code=500, detail="Database not connected")
    
    # Find the most recent poster for this event
    poster = await db.event_posters.find_one(
        {"event_id": event_id},
        sort=[("uploaded_at", -1)]  # Most recent first
    )
    
    if not poster:
        raise HTTPException(status_code=404, detail=f"No poster found for event {event_id}")
    
    # Return metadata without binary content
    return {
        "id": str(poster["_id"]),
        "event_id": poster["event_id"],
        "filename": poster["filename"],
        "content_type": poster["content_type"],
        "uploaded_at": poster["uploaded_at"].isoformat()
    }


@router.get("/event_poster/file/{poster_id}")
async def get_event_poster_file(poster_id: str):
    """
    Retrieve event poster file by poster ID.
    
    This endpoint retrieves the actual poster image file from the database. The file
    is streamed back to the client using FastAPI's StreamingResponse with the appropriate
    content-type header for proper browser rendering.
    
    File Retrieval Mechanism:
    - The binary content is retrieved from MongoDB
    - StreamingResponse is used to stream the file to the client
    - Content-Type header is set from stored metadata for proper browser handling
    - BytesIO is used to create a file-like object from the binary data
    
    Args:
        poster_id: String ID of the poster document
        
    Returns:
        StreamingResponse with the image file and proper headers
        
    Raises:
        HTTPException: 404 if poster not found, 400 if ID format is invalid
    """
    db = get_database()
    if db is None:
        raise HTTPException(status_code=500, detail="Database not connected")
    
    try:
        obj_id = validate_object_id(poster_id)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid poster ID format: {poster_id}")
    
    # Retrieve poster document
    poster = await db.event_posters.find_one({"_id": obj_id})
    
    if not poster:
        raise HTTPException(status_code=404, detail=f"Poster with ID {poster_id} not found")
    
    # Create file-like object from binary content
    file_content = BytesIO(poster["content"])
    
    # Return as streaming response with proper content type
    return StreamingResponse(
        file_content,
        media_type=poster.get("content_type", "image/jpeg"),
        headers={
            "Content-Disposition": f'inline; filename="{poster.get("filename", "poster")}"'
        }
    )

