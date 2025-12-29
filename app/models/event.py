"""
Event model
"""
from pydantic import BaseModel
from typing import Optional


class Event(BaseModel):
    """Event data model"""
    name: str
    description: str
    date: str
    venue_id: str
    max_attendees: int


class EventUpdate(BaseModel):
    """Event update model - all fields optional for partial updates"""
    name: Optional[str] = None
    description: Optional[str] = None
    date: Optional[str] = None
    venue_id: Optional[str] = None
    max_attendees: Optional[int] = None

