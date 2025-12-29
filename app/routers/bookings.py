"""
Booking-related API endpoints

This module handles all CRUD operations for ticket bookings:
- Create: POST /bookings - Creates a new booking
- Read: GET /bookings - Lists all bookings
- Read: GET /bookings/{booking_id} - Gets a specific booking by ID
- Update: PUT /bookings/{booking_id} - Updates a booking by ID
- Delete: DELETE /bookings/{booking_id} - Deletes a booking by ID

All operations interact with the MongoDB 'bookings' collection.
"""
from fastapi import APIRouter, HTTPException
from app.models.booking import Booking, BookingUpdate
from app.database import get_database, find_by_id, update_by_id, delete_by_id

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.post("", response_model=dict, status_code=201)
async def create_booking(booking: Booking):
    """
    Create a new booking.
    
    This endpoint creates a new ticket booking in the database. The booking data is validated
    using the Booking Pydantic model and then inserted into the MongoDB 'bookings' collection.
    
    Args:
        booking: Booking object containing event_id, attendee_id, ticket_type, and quantity
        
    Returns:
        Dictionary with success message and the created booking's ID
        
    Raises:
        HTTPException: 500 if database is not connected
    """
    db = get_database()
    if db is None:
        raise HTTPException(status_code=500, detail="Database not connected")
    
    booking_doc = booking.dict()
    result = await db.bookings.insert_one(booking_doc)
    return {"message": "Booking created", "id": str(result.inserted_id)}


@router.get("", response_model=list)
async def get_bookings():
    """
    Get all bookings.
    
    This endpoint retrieves all bookings from the database. It queries the MongoDB
    'bookings' collection and returns up to 100 bookings. Each booking's ObjectId is
    converted to a string for JSON serialization.
    
    Returns:
        List of booking dictionaries, each with _id converted to string
        
    Raises:
        HTTPException: 500 if database is not connected
    """
    db = get_database()
    if db is None:
        raise HTTPException(status_code=500, detail="Database not connected")
    
    bookings = await db.bookings.find().to_list(100)
    for booking in bookings:
        booking["_id"] = str(booking["_id"])
    return bookings


@router.get("/{booking_id}", response_model=dict)
async def get_booking(booking_id: str):
    """
    Get a specific booking by ID.
    
    This endpoint retrieves a single booking from the database by its ID. The ID
    is validated as a MongoDB ObjectId, and the booking is fetched from the 'bookings' collection.
    
    Args:
        booking_id: String representation of the booking's MongoDB ObjectId
        
    Returns:
        Booking dictionary with _id converted to string
        
    Raises:
        HTTPException: 404 if booking is not found, 400 if ID format is invalid
    """
    booking = await find_by_id("bookings", booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail=f"Booking with ID {booking_id} not found")
    return booking


@router.put("/{booking_id}", response_model=dict)
async def update_booking(booking_id: str, booking_update: BookingUpdate):
    """
    Update a booking by ID.
    
    This endpoint updates an existing booking in the database. Only the fields provided
    in the request body will be updated (partial update). The update data is validated
    using the BookingUpdate Pydantic model, which allows all fields to be optional.
    
    Args:
        booking_id: String representation of the booking's MongoDB ObjectId
        booking_update: BookingUpdate object with fields to update (all optional)
        
    Returns:
        Dictionary with success message
        
    Raises:
        HTTPException: 404 if booking is not found, 400 if ID format is invalid
    """
    # Check if booking exists
    booking = await find_by_id("bookings", booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail=f"Booking with ID {booking_id} not found")
    
    # Prepare update data (exclude None values)
    update_data = booking_update.dict(exclude_unset=True)
    
    # Perform update
    updated = await update_by_id("bookings", booking_id, update_data)
    if not updated:
        raise HTTPException(status_code=400, detail="No valid fields to update")
    
    return {"message": "Booking updated successfully", "id": booking_id}


@router.delete("/{booking_id}", response_model=dict)
async def delete_booking(booking_id: str):
    """
    Delete a booking by ID.
    
    This endpoint deletes a booking from the database. The booking is removed from
    the MongoDB 'bookings' collection by its ObjectId.
    
    Args:
        booking_id: String representation of the booking's MongoDB ObjectId
        
    Returns:
        Dictionary with success message
        
    Raises:
        HTTPException: 404 if booking is not found, 400 if ID format is invalid
    """
    deleted = await delete_by_id("bookings", booking_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Booking with ID {booking_id} not found")
    
    return {"message": "Booking deleted successfully", "id": booking_id}

