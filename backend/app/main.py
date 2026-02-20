from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import lectures_router, classes_router

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

@app.get("/")
def read_root():
    return {"message": "Lecture Management System API"}