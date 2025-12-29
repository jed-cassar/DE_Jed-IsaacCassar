"""
FastAPI application initialization

This module initializes the FastAPI application and includes all API routers.
It also handles database connection lifecycle using lifespan events.

Application Structure:
- FastAPI app instance with metadata (title, description, version)
- All API routers registered and included
- Lifespan context manager: Establishes and closes MongoDB connection

Note for Serverless Deployments (Vercel):
- Vercel supports FastAPI lifespan events natively
- Database connections are lazy-initialized on first request if lifespan doesn't run
"""
from contextlib import asynccontextmanager
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.
    
    Handles startup and shutdown logic for the application:
    - Startup: Establishes MongoDB connection
    - Shutdown: Closes MongoDB connection gracefully
    
    This is the modern FastAPI approach and is supported by Vercel.
    For serverless environments, if lifespan doesn't run, connections
    will be lazily initialized on first request.
    """
    # Startup: Connect to MongoDB
    try:
        await connect_to_mongo()
    except Exception as e:
        print(f"Warning: Could not connect to MongoDB during startup: {e}")
        print("Connection will be attempted on first request")
    
    yield
    
    # Shutdown: Close MongoDB connection
    await close_mongo_connection()


# Create FastAPI app instance with lifespan
# Metadata is used for API documentation (Swagger UI, ReDoc)
app = FastAPI(
    title="Event Management API",
    description="API for managing events, venues, attendees, and bookings with file upload/retrieval capabilities",
    version="1.0.0",
    lifespan=lifespan
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

