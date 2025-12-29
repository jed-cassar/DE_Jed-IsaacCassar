"""
Vercel serverless function entry point for FastAPI application

This file serves as the entry point for Vercel's serverless function deployment.
It uses Mangum to wrap the FastAPI ASGI application for serverless compatibility.

To deploy:
1. Install Vercel CLI: npm i -g vercel
2. Run: vercel
3. Set environment variables in Vercel dashboard:
   - MONGODB_URL: Your MongoDB connection string
   - DATABASE_NAME: Your database name

Note: Vercel serverless functions have execution time limits. For long-running
operations, consider using background jobs or alternative hosting solutions.
"""
from mangum import Mangum
from app.main import app

# Wrap FastAPI app with Mangum for serverless compatibility
handler = Mangum(app, lifespan="off")

# Export handler for Vercel
__all__ = ["handler"]

