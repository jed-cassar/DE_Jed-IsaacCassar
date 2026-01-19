"""
Venue model
"""
from pydantic import BaseModel
from typing import Optional


class Venue(BaseModel):
    """
    Venue data model for creating new venues.
    
    Design Decision: All fields are required to ensure complete venue information.
    Name and address are essential for identification and location, while capacity
    is necessary for event planning and booking validation.
    """
    # Required field: Venue name is essential for identification
    name: str
    # Required field: Address is needed for event location and attendee navigation
    # Note: Consider splitting into separate fields (street, city, state, zip) in future
    # for better searchability and structured data
    address: str
    # Required field: Capacity is critical for event capacity planning and booking limits
    # Must be a positive integer to make business logic sense
    capacity: int


class VenueUpdate(BaseModel):
    """
    Venue update model for partial updates.
    
    Design Decision: All fields are Optional to enable partial updates. This is
    especially useful when only the capacity needs updating (e.g., after renovations)
    or when correcting an address, without resending all venue data.
    
    Consideration: Capacity updates may affect existing events, but this is handled
    at the business logic layer rather than the model layer.
    """
    name: Optional[str] = None
    address: Optional[str] = None
    capacity: Optional[int] = None

