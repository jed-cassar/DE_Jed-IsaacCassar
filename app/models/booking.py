"""
Booking model
"""
from pydantic import BaseModel
from typing import Optional


class Booking(BaseModel):
    """
    Booking data model for creating new ticket bookings.
    
    Design Decision: All fields are required to ensure booking integrity. Each booking
    must link to both an event and an attendee, specify ticket type, and have a quantity.
    This prevents incomplete booking records that would cause data consistency issues.
    
    Future Enhancement: Consider adding validation to ensure quantity > 0 and that
    the referenced event_id and attendee_id actually exist (referential integrity).
    """
    # Required field: Links booking to the event being booked
    # Stored as string (MongoDB ObjectId) for referential integrity
    event_id: str
    # Required field: Links booking to the attendee making the booking
    # Stored as string (MongoDB ObjectId) for referential integrity
    attendee_id: str
    # Required field: Ticket type (e.g., "General", "VIP", "Student")
    # Design note: Consider making this an enum or reference to a ticket_types collection
    # for consistency across the application
    ticket_type: str
    # Required field: Number of tickets being booked
    # Must be a positive integer (consider adding validation)
    quantity: int


class BookingUpdate(BaseModel):
    """
    Booking update model for partial updates.
    
    Design Decision: All fields are Optional to allow partial updates. Common use cases:
    - Changing ticket quantity (e.g., adding more tickets)
    - Upgrading ticket type (e.g., General to VIP)
    - Transferring booking to different attendee
    
    Business Logic Note: Some updates may require additional validation:
    - Quantity increases must check event capacity
    - Attendee changes might require authorization checks
    - Event changes are typically not allowed (would require cancelling and creating new booking)
    """
    event_id: Optional[str] = None
    attendee_id: Optional[str] = None
    ticket_type: Optional[str] = None
    quantity: Optional[int] = None

