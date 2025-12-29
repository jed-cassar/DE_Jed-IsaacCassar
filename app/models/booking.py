"""
Booking model
"""
from pydantic import BaseModel


class Booking(BaseModel):
    """Booking data model"""
    event_id: str
    attendee_id: str
    ticket_type: str
    quantity: int

