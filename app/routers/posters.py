"""
Event poster upload endpoints
"""
from fastapi import APIRouter, File, UploadFile, HTTPException
from datetime import datetime
from app.database import get_database

router = APIRouter(prefix="/upload_event_poster", tags=["posters"])


@router.post("/{event_id}", response_model=dict)
async def upload_event_poster(event_id: str, file: UploadFile = File(...)):
    """Upload an event poster image"""
    db = get_database()
    if not db:
        raise HTTPException(status_code=500, detail="Database not connected")
    
    content = await file.read()
    poster_doc = {
        "event_id": event_id,
        "filename": file.filename,
        "content_type": file.content_type,
        "content": content,
        "uploaded_at": datetime.utcnow()
    }
    result = await db.event_posters.insert_one(poster_doc)
    return {"message": "Event poster uploaded", "id": str(result.inserted_id)}

