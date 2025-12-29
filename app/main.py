"""
FastAPI application initialization
"""
from fastapi import FastAPI
from app.database import connect_to_mongo, close_mongo_connection
from app.routers import events, posters

# Create FastAPI app instance
app = FastAPI(
    title="Event Management API",
    description="API for managing events, venues, attendees, and bookings",
    version="1.0.0"
)

# Include routers
app.include_router(events.router)
app.include_router(posters.router)


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

