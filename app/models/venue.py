"""
Venue model
"""
from pydantic import BaseModel
from typing import Optional


class Venue(BaseModel):
    """Venue data model"""
    name: str
    address: str
    capacity: int


class VenueUpdate(BaseModel):
    """Venue update model - all fields optional for partial updates"""
    name: Optional[str] = None
    address: Optional[str] = None
    capacity: Optional[int] = None

