"""
Attendee model
"""
from pydantic import BaseModel
from typing import Optional


class Attendee(BaseModel):
    """Attendee data model"""
    name: str
    email: str
    phone: Optional[str] = None


class AttendeeUpdate(BaseModel):
    """Attendee update model - all fields optional for partial updates"""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

