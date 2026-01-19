"""
Event model
"""
from pydantic import BaseModel
from typing import Optional


class Event(BaseModel):
    """
    Event data model for creating new events.
    
    Design Decision: All fields are required (non-optional) to ensure data integrity.
    This prevents creating incomplete event records that would require follow-up updates.
    When creating an event, we want to guarantee that all essential information is provided.
    """
    # Required field: Every event must have a name for identification and display
    name: str
    # Required field: Description helps users understand what the event is about
    description: str
    # Required field: Date is essential for event scheduling
    # Note: Using str type for flexibility with various date formats (ISO 8601 recommended)
    # Consider datetime type in future if stricter validation is needed
    date: str
    # Required field: Every event must be associated with a venue
    # Stored as string (MongoDB ObjectId) to maintain referential integrity
    venue_id: str
    # Required field: Maximum capacity is needed for booking validation and planning
    max_attendees: int


class EventUpdate(BaseModel):
    """
    Event update model for partial updates.
    
    Design Decision: Separate Update model with all Optional fields allows clients
    to update only specific fields without sending the entire object. This pattern
    supports PATCH-like behavior even though we use PUT endpoints.
    
    Why separate from Event model:
    1. Type safety: Prevents accidentally requiring fields that shouldn't be mandatory on update
    2. API clarity: Makes it explicit which fields can be updated
    3. Flexibility: Allows true partial updates without needing to send unchanged fields
    
    Implementation: Uses `exclude_unset=True` when converting to dict to only include
    fields that were explicitly provided in the request body.
    """
    # All fields optional: Client can update just the name, or any combination of fields
    name: Optional[str] = None
    description: Optional[str] = None
    date: Optional[str] = None
    venue_id: Optional[str] = None
    max_attendees: Optional[int] = None

