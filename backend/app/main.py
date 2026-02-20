import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import lectures_router, classes_router
from .routers import quizzes as quizzes_router
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI(title="Lecture Management System", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(classes_router, prefix="/classes", tags=["classes"])
app.include_router(lectures_router, prefix="/lectures", tags=["lectures"])
app.include_router(quizzes_router.router, prefix="/quizzes", tags=["quizzes"])

# Serve React static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
async def serve_react_index():
    return FileResponse(os.path.join(static_dir, "index.html"))

@app.get("/{full_path:path}")
async def serve_react_app(full_path: str):
    file_path = os.path.join(static_dir, full_path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)
    # Fallback to index.html for client-side routes
    return FileResponse(os.path.join(static_dir, "index.html"))