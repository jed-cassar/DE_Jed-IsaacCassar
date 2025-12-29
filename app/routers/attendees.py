"""
Attendee-related API endpoints

This module handles all CRUD operations for attendees:
- Create: POST /attendees - Creates a new attendee
- Read: GET /attendees - Lists all attendees
- Read: GET /attendees/{attendee_id} - Gets a specific attendee by ID
- Update: PUT /attendees/{attendee_id} - Updates an attendee by ID
- Delete: DELETE /attendees/{attendee_id} - Deletes an attendee by ID

All operations interact with the MongoDB 'attendees' collection.
"""
from fastapi import APIRouter, HTTPException
from app.models.attendee import Attendee, AttendeeUpdate
from app.database import get_database, find_by_id, update_by_id, delete_by_id

router = APIRouter(prefix="/attendees", tags=["attendees"])


@router.post("", response_model=dict, status_code=201)
async def create_attendee(attendee: Attendee):
    """
    Create a new attendee.
    
    This endpoint creates a new attendee in the database. The attendee data is validated
    using the Attendee Pydantic model and then inserted into the MongoDB 'attendees' collection.
    
    Args:
        attendee: Attendee object containing name, email, and optional phone
        
    Returns:
        Dictionary with success message and the created attendee's ID
        
    Raises:
        HTTPException: 500 if database is not connected
    """
    db = get_database()
    if not db:
        raise HTTPException(status_code=500, detail="Database not connected")
    
    attendee_doc = attendee.dict()
    result = await db.attendees.insert_one(attendee_doc)
    return {"message": "Attendee created", "id": str(result.inserted_id)}


@router.get("", response_model=list)
async def get_attendees():
    """
    Get all attendees.
    
    This endpoint retrieves all attendees from the database. It queries the MongoDB
    'attendees' collection and returns up to 100 attendees. Each attendee's ObjectId is
    converted to a string for JSON serialization.
    
    Returns:
        List of attendee dictionaries, each with _id converted to string
        
    Raises:
        HTTPException: 500 if database is not connected
    """
    db = get_database()
    if not db:
        raise HTTPException(status_code=500, detail="Database not connected")
    
    attendees = await db.attendees.find().to_list(100)
    for attendee in attendees:
        attendee["_id"] = str(attendee["_id"])
    return attendees


@router.get("/{attendee_id}", response_model=dict)
async def get_attendee(attendee_id: str):
    """
    Get a specific attendee by ID.
    
    This endpoint retrieves a single attendee from the database by its ID. The ID
    is validated as a MongoDB ObjectId, and the attendee is fetched from the 'attendees' collection.
    
    Args:
        attendee_id: String representation of the attendee's MongoDB ObjectId
        
    Returns:
        Attendee dictionary with _id converted to string
        
    Raises:
        HTTPException: 404 if attendee is not found, 400 if ID format is invalid
    """
    attendee = await find_by_id("attendees", attendee_id)
    if not attendee:
        raise HTTPException(status_code=404, detail=f"Attendee with ID {attendee_id} not found")
    return attendee


@router.put("/{attendee_id}", response_model=dict)
async def update_attendee(attendee_id: str, attendee_update: AttendeeUpdate):
    """
    Update an attendee by ID.
    
    This endpoint updates an existing attendee in the database. Only the fields provided
    in the request body will be updated (partial update). The update data is validated
    using the AttendeeUpdate Pydantic model, which allows all fields to be optional.
    
    Args:
        attendee_id: String representation of the attendee's MongoDB ObjectId
        attendee_update: AttendeeUpdate object with fields to update (all optional)
        
    Returns:
        Dictionary with success message
        
    Raises:
        HTTPException: 404 if attendee is not found, 400 if ID format is invalid
    """
    # Check if attendee exists
    attendee = await find_by_id("attendees", attendee_id)
    if not attendee:
        raise HTTPException(status_code=404, detail=f"Attendee with ID {attendee_id} not found")
    
    # Prepare update data (exclude None values)
    update_data = attendee_update.dict(exclude_unset=True)
    
    # Perform update
    updated = await update_by_id("attendees", attendee_id, update_data)
    if not updated:
        raise HTTPException(status_code=400, detail="No valid fields to update")
    
    return {"message": "Attendee updated successfully", "id": attendee_id}


@router.delete("/{attendee_id}", response_model=dict)
async def delete_attendee(attendee_id: str):
    """
    Delete an attendee by ID.
    
    This endpoint deletes an attendee from the database. The attendee is removed from
    the MongoDB 'attendees' collection by its ObjectId.
    
    Args:
        attendee_id: String representation of the attendee's MongoDB ObjectId
        
    Returns:
        Dictionary with success message
        
    Raises:
        HTTPException: 404 if attendee is not found, 400 if ID format is invalid
    """
    deleted = await delete_by_id("attendees", attendee_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Attendee with ID {attendee_id} not found")
    
    return {"message": "Attendee deleted successfully", "id": attendee_id}

