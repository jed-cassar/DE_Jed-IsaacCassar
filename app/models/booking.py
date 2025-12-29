"""
Booking model
"""
from pydantic import BaseModel
from typing import Optional


class Booking(BaseModel):
    """Booking data model"""
    event_id: str
    attendee_id: str
    ticket_type: str
    quantity: int


class BookingUpdate(BaseModel):
    """Booking update model - all fields optional for partial updates"""
    event_id: Optional[str] = None
    attendee_id: Optional[str] = None
    ticket_type: Optional[str] = None
    quantity: Optional[int] = None

