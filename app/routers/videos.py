"""
Promotional video upload and retrieval endpoints

This module handles uploading and retrieving promotional videos for events:
- Upload: POST /upload_promotional_video/{event_id} - Uploads a promotional video for an event
- Retrieve: GET /promotional_video/{event_id} - Retrieves video metadata by event ID
- Retrieve: GET /promotional_video/file/{video_id} - Retrieves video file by video ID

Files are stored in MongoDB 'promotional_videos' collection as binary data with metadata.
Note: MongoDB document size limit is 16MB. For larger videos, consider using GridFS.
"""
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from datetime import datetime
from bson import ObjectId
from io import BytesIO
from app.database import get_database, validate_object_id

router = APIRouter(tags=["videos"])


@router.post("/upload_promotional_video/{event_id}", response_model=dict, status_code=201)
async def upload_promotional_video(event_id: str, file: UploadFile = File(...)):
    """
    Upload a promotional video for an event.
    
    This endpoint uploads a promotional video file for a specific event. The video is stored
    in the MongoDB 'promotional_videos' collection as binary data along with metadata including
    the event_id, filename, content_type, and upload timestamp.
    
    File Storage Mechanism:
    - Videos are stored directly in MongoDB documents as binary data (BSON Binary type)
    - Each document contains: event_id, filename, content_type, content (binary), uploaded_at
    - MongoDB document size limit is 16MB - videos larger than this will fail
    - For larger videos, consider implementing GridFS (MongoDB's file storage system)
    
    Args:
        event_id: String ID of the event this video belongs to
        file: UploadFile object containing the video file
        
    Returns:
        Dictionary with success message and the video document ID
        
    Raises:
        HTTPException: 500 if database is not connected, 400 if file is too large or invalid
    """
    db = get_database()
    if db is None:
        raise HTTPException(status_code=500, detail="Database not connected")
    
    # Read file content
    content = await file.read()
    
    # Check file size (16MB MongoDB document limit)
    if len(content) > 16 * 1024 * 1024:  # 16MB
        raise HTTPException(
            status_code=400,
            detail="File size exceeds 16MB limit. Consider using GridFS for larger files."
        )
    
    # Create video document with binary content
    video_doc = {
        "event_id": event_id,
        "filename": file.filename,
        "content_type": file.content_type,
        "content": content,  # Stored as binary in MongoDB
        "uploaded_at": datetime.utcnow()
    }
    
    result = await db.promotional_videos.insert_one(video_doc)
    return {"message": "Promotional video uploaded", "id": str(result.inserted_id)}


@router.get("/promotional_video/{event_id}", response_model=dict)
async def get_promotional_video_metadata(event_id: str):
    """
    Get promotional video metadata by event ID.
    
    This endpoint retrieves the video metadata (not the file itself) for a specific event.
    It queries the 'promotional_videos' collection to find the most recent video for the event.
    
    Args:
        event_id: String ID of the event
        
    Returns:
        Dictionary with video metadata (excluding binary content)
        
    Raises:
        HTTPException: 404 if no video found for the event
    """
    db = get_database()
    if db is None:
        raise HTTPException(status_code=500, detail="Database not connected")
    
    # Find the most recent video for this event
    video = await db.promotional_videos.find_one(
        {"event_id": event_id},
        sort=[("uploaded_at", -1)]  # Most recent first
    )
    
    if not video:
        raise HTTPException(status_code=404, detail=f"No promotional video found for event {event_id}")
    
    # Return metadata without binary content
    return {
        "id": str(video["_id"]),
        "event_id": video["event_id"],
        "filename": video["filename"],
        "content_type": video["content_type"],
        "uploaded_at": video["uploaded_at"].isoformat()
    }


@router.get("/promotional_video/file/{video_id}")
async def get_promotional_video_file(video_id: str):
    """
    Retrieve promotional video file by video ID.
    
    This endpoint retrieves the actual video file from the database. The file
    is streamed back to the client using FastAPI's StreamingResponse with the appropriate
    content-type header for proper browser/media player handling.
    
    File Retrieval Mechanism:
    - The binary content is retrieved from MongoDB
    - StreamingResponse is used to stream the file to the client
    - Content-Type header is set from stored metadata (e.g., video/mp4, video/webm)
    - BytesIO is used to create a file-like object from the binary data
    - Content-Disposition header allows inline playback or download
    
    Args:
        video_id: String ID of the video document
        
    Returns:
        StreamingResponse with the video file and proper headers
        
    Raises:
        HTTPException: 404 if video not found, 400 if ID format is invalid
    """
    db = get_database()
    if db is None:
        raise HTTPException(status_code=500, detail="Database not connected")
    
    try:
        obj_id = validate_object_id(video_id)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid video ID format: {video_id}")
    
    # Retrieve video document
    video = await db.promotional_videos.find_one({"_id": obj_id})
    
    if not video:
        raise HTTPException(status_code=404, detail=f"Video with ID {video_id} not found")
    
    # Create file-like object from binary content
    file_content = BytesIO(video["content"])
    
    # Return as streaming response with proper content type
    return StreamingResponse(
        file_content,
        media_type=video.get("content_type", "video/mp4"),
        headers={
            "Content-Disposition": f'inline; filename="{video.get("filename", "video")}"'
        }
    )

