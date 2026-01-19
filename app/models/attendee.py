"""
Attendee model
"""
from pydantic import BaseModel
from typing import Optional


class Attendee(BaseModel):
    """
    Attendee data model for creating new attendees.
    
    Design Decision: Name and email are required as they are essential for attendee
    identification and communication. Phone is optional because not all attendees may
    want to provide it, and email is sufficient for primary communication.
    """
    # Required field: Name is essential for personalization and identification
    name: str
    # Required field: Email is primary contact method and used for ticket delivery
    # Note: Consider adding email validation using Pydantic's EmailStr in future
    email: str
    # Optional field: Phone number is secondary contact method
    # Design rationale: Making it optional improves user experience by reducing
    # required information, while still capturing phone when available
    phone: Optional[str] = None


class AttendeeUpdate(BaseModel):
    """
    Attendee update model for partial updates.
    
    Design Decision: All fields are Optional to support partial updates. This allows
    clients to update just the email, just the phone number, or any combination of fields
    without needing to provide all attendee information again.
    
    Trade-off: Email being optional in updates allows email correction, but doesn't
    prevent accidentally removing the email. Consider adding validation in the router
    to ensure at least one contact method remains if needed.
    """
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

