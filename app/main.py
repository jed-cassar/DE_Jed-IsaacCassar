"""
FastAPI application initialization

This module initializes the FastAPI application and includes all API routers.
It also handles database connection lifecycle (startup and shutdown events).
"""
from fastapi import FastAPI
from app.database import connect_to_mongo, close_mongo_connection
from app.routers import (
    events,
    attendees,
    venues,
    bookings,
    posters,
    videos,
    venue_photos
)

# Create FastAPI app instance
app = FastAPI(
    title="Event Management API",
    description="API for managing events, venues, attendees, and bookings with file upload/retrieval capabilities",
    version="1.0.0"
)

# Include all routers
app.include_router(events.router)
app.include_router(attendees.router)
app.include_router(venues.router)
app.include_router(bookings.router)
app.include_router(posters.router)
app.include_router(videos.router)
app.include_router(venue_photos.router)


@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup"""
    await connect_to_mongo()


@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown"""
    await close_mongo_connection()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Event Management API",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    from app.database import database
    from app.config import settings
    
    return {
        "status": "healthy",
        "database": settings.database_name,
        "connected": database is not None
    }

