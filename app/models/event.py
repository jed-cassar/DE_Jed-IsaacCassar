"""
Event model
"""
from pydantic import BaseModel


class Event(BaseModel):
    """Event data model"""
    name: str
    description: str
    date: str
    venue_id: str
    max_attendees: int

