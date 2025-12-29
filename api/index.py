"""
Vercel serverless function entry point for FastAPI application

This file serves as the entry point for Vercel's serverless function deployment.
Vercel supports FastAPI/ASGI applications natively, so we export the app directly.

To deploy:
1. Install Vercel CLI: npm i -g vercel
2. Run: vercel
3. Set environment variables in Vercel dashboard:
   - MONGODB_URL: Your MongoDB connection string
   - DATABASE_NAME: Your database name

Note: Vercel serverless functions have execution time limits. For long-running
operations, consider using background jobs or alternative hosting solutions.
"""
# Import the FastAPI app from the main application module
# Vercel's Python runtime will detect the 'app' variable and use it as the ASGI handler
from app.main import app

# Ensure app is available at module level for Vercel to detect
# Vercel supports ASGI apps directly, no adapter needed

