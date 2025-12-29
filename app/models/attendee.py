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

