from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, Base
from . import models  # noqa: F401 - imported for SQLAlchemy model registration

# Create all database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Amendment Tracking System",
    description=(
        "Internal amendment tracking system for managing application updates"
    ),
    version="1.0.0",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {
        "message": "Amendment Tracking System API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
