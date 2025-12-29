"""
Event-related API endpoints

This module handles all CRUD operations for events:
- Create: POST /events - Creates a new event
- Read: GET /events - Lists all events
- Read: GET /events/{event_id} - Gets a specific event by ID
- Update: PUT /events/{event_id} - Updates an event by ID
- Delete: DELETE /events/{event_id} - Deletes an event by ID

All operations interact with the MongoDB 'events' collection.
"""
from fastapi import APIRouter, HTTPException
from app.models.event import Event, EventUpdate
from app.database import ensure_database, find_by_id, update_by_id, delete_by_id

router = APIRouter(prefix="/events", tags=["events"])


@router.post("", response_model=dict, status_code=201)
async def create_event(event: Event):
    """
    Create a new event.
    
    This endpoint creates a new event in the database. The event data is validated
    using the Event Pydantic model and then inserted into the MongoDB 'events' collection.
    
    Args:
        event: Event object containing name, description, date, venue_id, and max_attendees
        
    Returns:
        Dictionary with success message and the created event's ID
        
    Raises:
        HTTPException: 500 if database is not connected
    """
    db = await ensure_database()
    
    event_doc = event.dict()
    result = await db.events.insert_one(event_doc)
    return {"message": "Event created", "id": str(result.inserted_id)}


@router.get("", response_model=list)
async def get_events():
    """
    Get all events.
    
    This endpoint retrieves all events from the database. It queries the MongoDB
    'events' collection and returns up to 100 events. Each event's ObjectId is
    converted to a string for JSON serialization.
    
    Returns:
        List of event dictionaries, each with _id converted to string
        
    Raises:
        HTTPException: 500 if database is not connected
    """
    db = await ensure_database()
    
    events = await db.events.find().to_list(100)
    for event in events:
        event["_id"] = str(event["_id"])
    return events


@router.get("/{event_id}", response_model=dict)
async def get_event(event_id: str):
    """
    Get a specific event by ID.
    
    This endpoint retrieves a single event from the database by its ID. The ID
    is validated as a MongoDB ObjectId, and the event is fetched from the 'events' collection.
    
    Args:
        event_id: String representation of the event's MongoDB ObjectId
        
    Returns:
        Event dictionary with _id converted to string
        
    Raises:
        HTTPException: 404 if event is not found, 400 if ID format is invalid
    """
    event = await find_by_id("events", event_id)
    if not event:
        raise HTTPException(status_code=404, detail=f"Event with ID {event_id} not found")
    return event


@router.put("/{event_id}", response_model=dict)
async def update_event(event_id: str, event_update: EventUpdate):
    """
    Update an event by ID.
    
    This endpoint updates an existing event in the database. Only the fields provided
    in the request body will be updated (partial update). The update data is validated
    using the EventUpdate Pydantic model, which allows all fields to be optional.
    
    Args:
        event_id: String representation of the event's MongoDB ObjectId
        event_update: EventUpdate object with fields to update (all optional)
        
    Returns:
        Dictionary with success message
        
    Raises:
        HTTPException: 404 if event is not found, 400 if ID format is invalid
    """
    # Check if event exists
    event = await find_by_id("events", event_id)
    if not event:
        raise HTTPException(status_code=404, detail=f"Event with ID {event_id} not found")
    
    # Prepare update data (exclude None values)
    update_data = event_update.dict(exclude_unset=True)
    
    # Perform update
    updated = await update_by_id("events", event_id, update_data)
    if not updated:
        raise HTTPException(status_code=400, detail="No valid fields to update")
    
    return {"message": "Event updated successfully", "id": event_id}


@router.delete("/{event_id}", response_model=dict)
async def delete_event(event_id: str):
    """
    Delete an event by ID.
    
    This endpoint deletes an event from the database. The event is removed from
    the MongoDB 'events' collection by its ObjectId.
    
    Args:
        event_id: String representation of the event's MongoDB ObjectId
        
    Returns:
        Dictionary with success message
        
    Raises:
        HTTPException: 404 if event is not found, 400 if ID format is invalid
    """
    deleted = await delete_by_id("events", event_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Event with ID {event_id} not found")
    
    return {"message": "Event deleted successfully", "id": event_id}

