"""
FastAPI application initialization

This module initializes the FastAPI application and includes all API routers.
It also handles database connection lifecycle (startup and shutdown events).

Application Structure:
- FastAPI app instance with metadata (title, description, version)
- All API routers registered and included
- Startup event: Establishes MongoDB connection
- Shutdown event: Closes MongoDB connection gracefully

Note for Serverless Deployments (Vercel):
- The Mangum adapter in api/index.py uses lifespan="off"
- This disables startup/shutdown events for serverless compatibility
- Database connections may need to be handled per-request in serverless environments
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
# Metadata is used for API documentation (Swagger UI, ReDoc)
app = FastAPI(
    title="Event Management API",
    description="API for managing events, venues, attendees, and bookings with file upload/retrieval capabilities",
    version="1.0.0"
)

# Include all API routers
# Each router handles a specific resource or feature set
app.include_router(events.router)           # Event CRUD operations
app.include_router(attendees.router)        # Attendee CRUD operations
app.include_router(venues.router)           # Venue CRUD operations
app.include_router(bookings.router)        # Booking CRUD operations
app.include_router(posters.router)         # Event poster file upload/retrieval
app.include_router(videos.router)          # Promotional video file upload/retrieval
app.include_router(venue_photos.router)     # Venue photo file upload/retrieval


@app.on_event("startup")
async def startup_event():
    """
    Initialize database connection on application startup.
    
    This event handler is called once when the FastAPI application starts.
    It establishes the MongoDB connection that will be reused for all requests.
    
    Lifecycle:
    - Called automatically by FastAPI when app starts
    - Runs before any requests are processed
    - Connection is stored in global variables for reuse
    
    Note: For serverless deployments (Vercel), this may not run due to
    lifespan="off" in Mangum adapter. In such cases, connections may need
    to be established per-request or using connection pooling.
    """
    await connect_to_mongo()


@app.on_event("shutdown")
async def shutdown_event():
    """
    Close database connection on application shutdown.
    
    This event handler is called when the FastAPI application is shutting down.
    It properly closes the MongoDB connection and releases resources.
    
    Lifecycle:
    - Called automatically by FastAPI when app shuts down
    - Runs after all requests are processed
    - Ensures clean disconnection from database
    
    Note: For serverless deployments, this may not run. Connections may be
    closed automatically when the function execution ends.
    """
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

