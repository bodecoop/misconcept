# Lecture Management System Backend

A production-ready REST API backend for managing lecture uploads and metadata using FastAPI and Oracle Database.

## Features

- User authentication (register/login) with JWT tokens
- Upload lecture PDF files and transcript text files
- Store metadata: class name, lecture title, date, labels/tags
- Oracle database integration with connection pooling
- File validation and secure storage
- Modular architecture with proper error handling

## Requirements

- Python 3.8+
- Oracle Database
- Oracle Instant Client (for oracledb driver)

## Installation

1. Clone the repository and navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Fill in your Oracle database connection details and JWT secret

5. Create database tables:
   - Run the SQL script in `create_tables.sql` in your Oracle database

## Running the Application

Start the server with:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once running, visit `http://localhost:8000/docs` for interactive API documentation.

## API Endpoints


### Authentication
- `POST /auth/register` — Register a new user
- `POST /auth/login` — Login and get JWT token

### Classes (require authentication)
- `POST /classes/` — Create a new class
- `GET /classes/` — Get all classes
- `GET /classes/{class_id}` — Get a specific class by ID
- `DELETE /classes/{class_id}` — Delete a class and all its dependent lectures, files, and labels

### Lectures (require authentication)
- `POST /lectures/upload` — Upload lecture files and metadata
- `GET /lectures/` — Get all lectures
- `GET /lectures/{lecture_id}` — Get specific lecture by ID
- `DELETE /lectures/{lecture_id}` — Delete a lecture

## Database Schema

- `users` - User accounts
- `lectures` - Lecture metadata and file paths
- `lecture_labels` - Labels/tags for lectures