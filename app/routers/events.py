"""
Event-related API endpoints
"""
from fastapi import APIRouter, HTTPException
from app.models.event import Event
from app.database import get_database

router = APIRouter(prefix="/events", tags=["events"])


@router.post("", response_model=dict)
async def create_event(event: Event):
    """Create a new event"""
    db = get_database()
    if not db:
        raise HTTPException(status_code=500, detail="Database not connected")
    
    event_doc = event.dict()
    result = await db.events.insert_one(event_doc)
    return {"message": "Event created", "id": str(result.inserted_id)}


@router.get("", response_model=list)
async def get_events():
    """Get all events"""
    db = get_database()
    if not db:
        raise HTTPException(status_code=500, detail="Database not connected")
    
    events = await db.events.find().to_list(100)
    for event in events:
        event["_id"] = str(event["_id"])
    return events

