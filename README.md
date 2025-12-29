# Event Management API

A comprehensive FastAPI-based REST API for managing events, venues, attendees, bookings, and associated media files (posters, videos, venue photos).

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [API Endpoints](#api-endpoints)
- [Database Schema](#database-schema)
- [File Storage](#file-storage)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the API](#running-the-api)
- [Testing with Postman](#testing-with-postman)
- [Deployment](#deployment)
- [API Documentation](#api-documentation)

## Overview

This API provides a complete event management system with the following capabilities:

- **CRUD Operations**: Full Create, Read, Update, Delete operations for events, attendees, venues, and bookings
- **File Management**: Upload and retrieve event posters, promotional videos, and venue photos
- **MongoDB Integration**: Uses Motor (async MongoDB driver) for efficient database operations
- **RESTful Design**: Follows REST principles with proper HTTP methods and status codes
- **Auto Documentation**: Interactive API documentation via Swagger UI

## Features

### Core Functionality
- ✅ Event management (create, read, update, delete)
- ✅ Attendee management (create, read, update, delete)
- ✅ Venue management (create, read, update, delete)
- ✅ Booking management (create, read, update, delete)
- ✅ Event poster upload and retrieval
- ✅ Promotional video upload and retrieval
- ✅ Venue photo upload and retrieval (multiple photos per venue)

### Technical Features
- Async/await for high performance
- Pydantic models for data validation
- Comprehensive error handling
- MongoDB ObjectId validation
- File streaming for efficient file delivery
- Environment-based configuration

## API Endpoints

### Events

#### Create Event
```
POST /events
Content-Type: application/json

{
  "name": "Summer Music Festival",
  "description": "Annual summer music festival",
  "date": "2024-07-15",
  "venue_id": "507f1f77bcf86cd799439011",
  "max_attendees": 5000
}
```

**Response:** `201 Created`
```json
{
  "message": "Event created",
  "id": "507f1f77bcf86cd799439012"
}
```

#### Get All Events
```
GET /events
```

**Response:** `200 OK`
```json
[
  {
    "_id": "507f1f77bcf86cd799439012",
    "name": "Summer Music Festival",
    "description": "Annual summer music festival",
    "date": "2024-07-15",
    "venue_id": "507f1f77bcf86cd799439011",
    "max_attendees": 5000
  }
]
```

#### Get Event by ID
```
GET /events/{event_id}
```

**Response:** `200 OK` - Event object
**Error:** `404 Not Found` - If event doesn't exist

#### Update Event
```
PUT /events/{event_id}
Content-Type: application/json

{
  "name": "Summer Music Festival 2024",
  "max_attendees": 6000
}
```

**Response:** `200 OK`
```json
{
  "message": "Event updated successfully",
  "id": "507f1f77bcf86cd799439012"
}
```

#### Delete Event
```
DELETE /events/{event_id}
```

**Response:** `200 OK`
```json
{
  "message": "Event deleted successfully",
  "id": "507f1f77bcf86cd799439012"
}
```

### Attendees

#### Create Attendee
```
POST /attendees
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+1234567890"
}
```

#### Get All Attendees
```
GET /attendees
```

#### Get Attendee by ID
```
GET /attendees/{attendee_id}
```

#### Update Attendee
```
PUT /attendees/{attendee_id}
Content-Type: application/json

{
  "email": "newemail@example.com"
}
```

#### Delete Attendee
```
DELETE /attendees/{attendee_id}
```

### Venues

#### Create Venue
```
POST /venues
Content-Type: application/json

{
  "name": "Convention Center",
  "address": "123 Main St, City, State",
  "capacity": 10000
}
```

#### Get All Venues
```
GET /venues
```

#### Get Venue by ID
```
GET /venues/{venue_id}
```

#### Update Venue
```
PUT /venues/{venue_id}
Content-Type: application/json

{
  "capacity": 12000
}
```

#### Delete Venue
```
DELETE /venues/{venue_id}
```

### Bookings

#### Create Booking
```
POST /bookings
Content-Type: application/json

{
  "event_id": "507f1f77bcf86cd799439012",
  "attendee_id": "507f1f77bcf86cd799439013",
  "ticket_type": "VIP",
  "quantity": 2
}
```

#### Get All Bookings
```
GET /bookings
```

#### Get Booking by ID
```
GET /bookings/{booking_id}
```

#### Update Booking
```
PUT /bookings/{booking_id}
Content-Type: application/json

{
  "quantity": 3
}
```

#### Delete Booking
```
DELETE /bookings/{booking_id}
```

### File Upload/Retrieval

#### Upload Event Poster
```
POST /upload_event_poster/{event_id}
Content-Type: multipart/form-data

file: [binary image data]
```

**Response:** `201 Created`
```json
{
  "message": "Event poster uploaded",
  "id": "507f1f77bcf86cd799439014"
}
```

#### Get Event Poster Metadata
```
GET /event_poster/{event_id}
```

**Response:** `200 OK`
```json
{
  "id": "507f1f77bcf86cd799439014",
  "event_id": "507f1f77bcf86cd799439012",
  "filename": "poster.jpg",
  "content_type": "image/jpeg",
  "uploaded_at": "2024-01-15T10:30:00"
}
```

#### Get Event Poster File
```
GET /event_poster/file/{poster_id}
```

**Response:** `200 OK` - Image file streamed with appropriate content-type

#### Upload Promotional Video
```
POST /upload_promotional_video/{event_id}
Content-Type: multipart/form-data

file: [binary video data]
```

**Note:** Video files must be under 16MB (MongoDB document limit)

#### Get Promotional Video Metadata
```
GET /promotional_video/{event_id}
```

#### Get Promotional Video File
```
GET /promotional_video/file/{video_id}
```

#### Upload Venue Photo
```
POST /upload_venue_photo/{venue_id}
Content-Type: multipart/form-data

file: [binary image data]
```

#### Get All Venue Photos (Metadata)
```
GET /venue_photos/{venue_id}
```

**Response:** `200 OK` - Array of photo metadata objects

#### Get Venue Photo File
```
GET /venue_photo/file/{photo_id}
```

## Database Schema

### Collections

#### events
```json
{
  "_id": ObjectId,
  "name": String,
  "description": String,
  "date": String,
  "venue_id": String,
  "max_attendees": Integer
}
```

#### attendees
```json
{
  "_id": ObjectId,
  "name": String,
  "email": String,
  "phone": String (optional)
}
```

#### venues
```json
{
  "_id": ObjectId,
  "name": String,
  "address": String,
  "capacity": Integer
}
```

#### bookings
```json
{
  "_id": ObjectId,
  "event_id": String,
  "attendee_id": String,
  "ticket_type": String,
  "quantity": Integer
}
```

#### event_posters
```json
{
  "_id": ObjectId,
  "event_id": String,
  "filename": String,
  "content_type": String,
  "content": Binary,
  "uploaded_at": DateTime
}
```

#### promotional_videos
```json
{
  "_id": ObjectId,
  "event_id": String,
  "filename": String,
  "content_type": String,
  "content": Binary,
  "uploaded_at": DateTime
}
```

#### venue_photos
```json
{
  "_id": ObjectId,
  "venue_id": String,
  "filename": String,
  "content_type": String,
  "content": Binary,
  "uploaded_at": DateTime
}
```

## File Storage

### Storage Mechanism

Files (posters, videos, venue photos) are stored directly in MongoDB documents as binary data (BSON Binary type). Each file document contains:

- **Metadata**: filename, content_type, uploaded_at timestamp
- **Binary Content**: The actual file data stored as BSON Binary
- **Reference**: event_id or venue_id linking the file to its parent entity

### Storage Process

1. **Upload**: Client sends file via multipart/form-data
2. **Processing**: Server reads file content into memory
3. **Storage**: File is stored in MongoDB collection with metadata
4. **Response**: Server returns document ID for future retrieval

### Retrieval Process

1. **Request**: Client requests file by ID or parent entity ID
2. **Query**: Server queries MongoDB collection
3. **Streaming**: File content is streamed using FastAPI's `StreamingResponse`
4. **Headers**: Proper content-type and content-disposition headers are set
5. **Delivery**: File is streamed to client for display or download

### Limitations

- **Document Size Limit**: MongoDB documents have a 16MB size limit
- **Suitable For**: Images (posters, photos) and small videos
- **Not Suitable For**: Large video files (>16MB)
- **Alternative**: For larger files, consider MongoDB GridFS (not implemented in this version)

### File Retrieval Endpoints

All file retrieval endpoints use `StreamingResponse` which:
- Efficiently streams large files without loading entirely into memory
- Sets appropriate `Content-Type` headers for browser/media player compatibility
- Supports inline display or download via `Content-Disposition` headers

## Installation

### Prerequisites

- Python 3.9 or higher
- MongoDB database (local or MongoDB Atlas)
- pip (Python package manager)

### Steps

1. **Clone the repository** (or navigate to project directory)

2. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**

Create a `.env` file in the project root:
```env
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=event_management_db
```

For MongoDB Atlas:
```env
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/
DATABASE_NAME=event_management_db
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MONGODB_URL` | MongoDB connection string | `your_mongo_connection_string` |
| `DATABASE_NAME` | Name of the database | `event_management_db` |

### Configuration File

Configuration is managed in `app/config.py` using Pydantic Settings, which:
- Loads from `.env` file automatically
- Validates environment variables
- Provides type-safe configuration access

## Running the API

### Development Mode

```bash
# Activate virtual environment
source venv/bin/activate

# Run with auto-reload
uvicorn main:app --reload
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Testing with Postman

### Setting Up Postman

1. **Import Collection** (optional):
   - Create a new collection in Postman
   - Add requests for each endpoint

2. **Base URL**: `http://localhost:8000` (local) or your deployed URL

3. **Common Headers**:
   - `Content-Type: application/json` (for JSON requests)
   - `Content-Type: multipart/form-data` (for file uploads)

### Example Requests

#### Create Event
- **Method**: POST
- **URL**: `http://localhost:8000/events`
- **Headers**: `Content-Type: application/json`
- **Body** (raw JSON):
```json
{
  "name": "Tech Conference 2024",
  "description": "Annual technology conference",
  "date": "2024-09-20",
  "venue_id": "507f1f77bcf86cd799439011",
  "max_attendees": 1000
}
```

#### Upload Event Poster
- **Method**: POST
- **URL**: `http://localhost:8000/upload_event_poster/{event_id}`
- **Body**: form-data
  - Key: `file`, Type: File
  - Value: Select image file

#### Get Event Poster File
- **Method**: GET
- **URL**: `http://localhost:8000/event_poster/file/{poster_id}`
- **Response**: Image file (can be viewed in Postman or browser)

### Testing Checklist

- [ ] Create event, attendee, venue, booking
- [ ] Retrieve all items for each entity type
- [ ] Retrieve single item by ID
- [ ] Update each entity type
- [ ] Delete each entity type
- [ ] Upload event poster
- [ ] Retrieve event poster metadata
- [ ] Retrieve event poster file
- [ ] Upload promotional video
- [ ] Retrieve promotional video
- [ ] Upload venue photo
- [ ] List venue photos
- [ ] Retrieve venue photo file
- [ ] Test error cases (404, 400, 500)

## Deployment

### Vercel Deployment

#### Prerequisites
- Vercel account
- Vercel CLI installed: `npm i -g vercel`

#### Steps

1. **Install Vercel CLI** (if not already installed)
```bash
npm i -g vercel
```

2. **Login to Vercel**
```bash
vercel login
```

3. **Deploy**
```bash
vercel
```

4. **Set Environment Variables**

In Vercel dashboard:
- Go to Project Settings → Environment Variables
- Add:
  - `MONGODB_URL`: Your MongoDB connection string
  - `DATABASE_NAME`: Your database name

5. **Redeploy** (if needed after setting environment variables)
```bash
vercel --prod
```

#### Vercel Configuration

The project includes:
- `vercel.json`: Vercel configuration file
- `api/index.py`: Serverless function entry point using Mangum adapter

**Mangum Adapter**: The API uses Mangum to wrap the FastAPI ASGI application for serverless compatibility. This allows FastAPI to work seamlessly with Vercel's serverless function runtime.

**Note**: Vercel serverless functions have execution time limits. For production workloads with long-running operations, consider alternative hosting solutions like:
- Railway
- Render
- Fly.io
- Heroku

### Alternative Deployment Options

#### Railway
1. Connect GitHub repository
2. Set environment variables
3. Deploy automatically

#### Render
1. Create new Web Service
2. Connect repository
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Set environment variables

## API Documentation

### Interactive Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
  - Interactive interface for testing endpoints
  - View request/response schemas
  - Try out endpoints directly in browser

- **ReDoc**: http://localhost:8000/redoc
  - Alternative documentation interface
  - Clean, readable format

### OpenAPI Schema

The OpenAPI schema is available at:
- **JSON**: http://localhost:8000/openapi.json
- **YAML**: http://localhost:8000/openapi.yaml

### Endpoint Documentation

Each endpoint includes:
- **Purpose**: What the endpoint does
- **Request Format**: Expected request body/parameters
- **Response Format**: Response structure and status codes
- **Database Interaction**: How it interacts with MongoDB
- **File Handling**: How files are stored/retrieved (for file endpoints)

## Error Handling

The API uses consistent error responses:

### Status Codes

- `200 OK`: Successful GET, PUT, DELETE
- `201 Created`: Successful POST (creation)
- `400 Bad Request`: Invalid request data or ID format
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Database connection issues

### Error Response Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common Errors

- **Invalid ID Format**: `400 Bad Request` - "Invalid ID format: {id}"
- **Resource Not Found**: `404 Not Found` - "{Resource} with ID {id} not found"
- **Database Not Connected**: `500 Internal Server Error` - "Database not connected"
- **File Too Large**: `400 Bad Request` - "File size exceeds 16MB limit"

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app initialization
│   ├── config.py            # Configuration settings
│   ├── database.py          # Database connection and helpers
│   ├── models/              # Pydantic models
│   │   ├── __init__.py
│   │   ├── event.py
│   │   ├── attendee.py
│   │   ├── venue.py
│   │   └── booking.py
│   └── routers/             # API route handlers
│       ├── __init__.py
│       ├── events.py
│       ├── attendees.py
│       ├── venues.py
│       ├── bookings.py
│       ├── posters.py
│       ├── videos.py
│       └── venue_photos.py
├── api/
│   └── index.py             # Vercel serverless entry point
├── main.py                  # Application entry point
├── requirements.txt         # Python dependencies
├── vercel.json              # Vercel configuration
├── .env                     # Environment variables (not in git)
└── README.md                # This file
```

## License

This project is part of a Database Essentials assignment.

## Support

For issues or questions, please refer to the assignment documentation or contact your instructor.

