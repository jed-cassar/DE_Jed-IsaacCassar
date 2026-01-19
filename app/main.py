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
    # Design Decision: Lifespan pattern is the modern FastAPI way to handle
    # startup/shutdown logic. It's cleaner than deprecated startup/shutdown events
    # and provides proper async context management. This pattern is supported
    # by Vercel for serverless deployments.
    try:
        await connect_to_mongo()
    except Exception as e:
        # Design Decision: Don't fail application startup if database connection fails
        # In serverless environments (Vercel), connections may be established on first
        # request via ensure_database(). This graceful degradation allows the app to
        # start even if connection fails, with connections retried on first request.
        print(f"Warning: Could not connect to MongoDB during startup: {e}")
        print("Connection will be attempted on first request")
    
    yield
    # Design Decision: The 'yield' statement separates startup from shutdown logic
    # Code before yield runs on startup, code after runs on shutdown
    
    # Shutdown: Close MongoDB connection
    # Design Decision: Always close connection on shutdown to release resources
    # In serverless environments, this ensures connections are properly closed
    # when the function container is terminated
    await close_mongo_connection()


# Create FastAPI app instance with lifespan
# Design Decision: Metadata (title, description, version) is used for:
# - API documentation auto-generation (Swagger UI at /docs, ReDoc at /redoc)
# - API versioning and identification
# - Client SDK generation tools
# Design Decision: Using lifespan parameter for startup/shutdown logic
# This is the modern FastAPI pattern, replacing deprecated startup/shutdown events
app = FastAPI(
    title="Event Management API",
    description="API for managing events, venues, attendees, and bookings with file upload/retrieval capabilities",
    version="1.0.0",
    lifespan=lifespan
)

# Include all API routers
# Design Decision: Each router handles a specific resource or feature set
# This modular organization separates concerns and makes the codebase maintainable:
# - CRUD routers (events, attendees, venues, bookings) handle data operations
# - File routers (posters, videos, venue_photos) handle file upload/retrieval
# Design Decision: Router order doesn't matter for routing, but consistent
# ordering improves code readability and makes it easier to find specific routes
# Design Decision: Tags are defined in routers for API documentation grouping
app.include_router(events.router)           # Event CRUD operations - /events
app.include_router(attendees.router)        # Attendee CRUD operations - /attendees
app.include_router(venues.router)           # Venue CRUD operations - /venues
app.include_router(bookings.router)        # Booking CRUD operations - /bookings
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
    """
    Health check endpoint for monitoring and load balancers.
    
    Design Decision: Health check endpoint is essential for:
    - Container orchestration (Kubernetes, Docker Swarm) to determine if service is ready
    - Load balancers to route traffic away from unhealthy instances
    - Monitoring systems to track service availability
    - Vercel serverless deployments to ensure functions are responding
    
    Design Decision: Import inside function to avoid circular imports
    - database and settings are imported locally to prevent import-time evaluation
    - This is safe because these are used only when the endpoint is called
    
    Design Decision: Return database connection status
    - "connected" field indicates if database connection is established
    - In serverless environments, this may be False until first request triggers connection
    - Health check doesn't verify actual database accessibility (ping) to keep it lightweight
    """
    from app.database import database
    from app.config import settings
    
    # Design Decision: Simple health check returns connection status
    # For production, consider adding database ping to verify actual connectivity
    # Trade-off: Lightweight check (fast) vs. comprehensive check (accurate)
    return {
        "status": "healthy",
        "database": settings.database_name,
        "connected": database is not None
    }

