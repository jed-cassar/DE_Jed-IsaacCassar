"""
Venue model
"""
from pydantic import BaseModel


class Venue(BaseModel):
    """Venue data model"""
    name: str
    address: str
    capacity: int

