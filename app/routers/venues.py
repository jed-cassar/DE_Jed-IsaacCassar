"""
Venue-related API endpoints

This module handles all CRUD operations for venues:
- Create: POST /venues - Creates a new venue
- Read: GET /venues - Lists all venues
- Read: GET /venues/{venue_id} - Gets a specific venue by ID
- Update: PUT /venues/{venue_id} - Updates a venue by ID
- Delete: DELETE /venues/{venue_id} - Deletes a venue by ID

All operations interact with the MongoDB 'venues' collection.
"""
from fastapi import APIRouter, HTTPException
from app.models.venue import Venue, VenueUpdate
from app.database import ensure_database, find_by_id, update_by_id, delete_by_id

router = APIRouter(prefix="/venues", tags=["venues"])


@router.post("", response_model=dict, status_code=201)
async def create_venue(venue: Venue):
    """
    Create a new venue.
    
    This endpoint creates a new venue in the database. The venue data is validated
    using the Venue Pydantic model and then inserted into the MongoDB 'venues' collection.
    
    Args:
        venue: Venue object containing name, address, and capacity
        
    Returns:
        Dictionary with success message and the created venue's ID
        
    Raises:
        HTTPException: 500 if database is not connected
    """
    db = await ensure_database()
    
    venue_doc = venue.dict()
    result = await db.venues.insert_one(venue_doc)
    return {"message": "Venue created", "id": str(result.inserted_id)}


@router.get("", response_model=list)
async def get_venues():
    """
    Get all venues.
    
    This endpoint retrieves all venues from the database. It queries the MongoDB
    'venues' collection and returns up to 100 venues. Each venue's ObjectId is
    converted to a string for JSON serialization.
    
    Returns:
        List of venue dictionaries, each with _id converted to string
        
    Raises:
        HTTPException: 500 if database is not connected
    """
    db = await ensure_database()
    
    venues = await db.venues.find().to_list(100)
    for venue in venues:
        venue["_id"] = str(venue["_id"])
    return venues


@router.get("/{venue_id}", response_model=dict)
async def get_venue(venue_id: str):
    """
    Get a specific venue by ID.
    
    This endpoint retrieves a single venue from the database by its ID. The ID
    is validated as a MongoDB ObjectId, and the venue is fetched from the 'venues' collection.
    
    Args:
        venue_id: String representation of the venue's MongoDB ObjectId
        
    Returns:
        Venue dictionary with _id converted to string
        
    Raises:
        HTTPException: 404 if venue is not found, 400 if ID format is invalid
    """
    venue = await find_by_id("venues", venue_id)
    if not venue:
        raise HTTPException(status_code=404, detail=f"Venue with ID {venue_id} not found")
    return venue


@router.put("/{venue_id}", response_model=dict)
async def update_venue(venue_id: str, venue_update: VenueUpdate):
    """
    Update a venue by ID.
    
    This endpoint updates an existing venue in the database. Only the fields provided
    in the request body will be updated (partial update). The update data is validated
    using the VenueUpdate Pydantic model, which allows all fields to be optional.
    
    Args:
        venue_id: String representation of the venue's MongoDB ObjectId
        venue_update: VenueUpdate object with fields to update (all optional)
        
    Returns:
        Dictionary with success message
        
    Raises:
        HTTPException: 404 if venue is not found, 400 if ID format is invalid
    """
    # Check if venue exists
    venue = await find_by_id("venues", venue_id)
    if not venue:
        raise HTTPException(status_code=404, detail=f"Venue with ID {venue_id} not found")
    
    # Prepare update data (exclude None values)
    update_data = venue_update.dict(exclude_unset=True)
    
    # Perform update
    updated = await update_by_id("venues", venue_id, update_data)
    if not updated:
        raise HTTPException(status_code=400, detail="No valid fields to update")
    
    return {"message": "Venue updated successfully", "id": venue_id}


@router.delete("/{venue_id}", response_model=dict)
async def delete_venue(venue_id: str):
    """
    Delete a venue by ID.
    
    This endpoint deletes a venue from the database. The venue is removed from
    the MongoDB 'venues' collection by its ObjectId.
    
    Args:
        venue_id: String representation of the venue's MongoDB ObjectId
        
    Returns:
        Dictionary with success message
        
    Raises:
        HTTPException: 404 if venue is not found, 400 if ID format is invalid
    """
    deleted = await delete_by_id("venues", venue_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Venue with ID {venue_id} not found")
    
    return {"message": "Venue deleted successfully", "id": venue_id}

