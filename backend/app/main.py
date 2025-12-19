"""
Main FastAPI application for the Amendment Tracking System.
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import init_db, check_db_connection
from . import models  # noqa: F401 - imported for SQLAlchemy model registration


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Handles startup and shutdown events:
    - Startup: Initialize database and check connection
    - Shutdown: Cleanup resources
    """
    # Startup
    print("Starting Amendment Tracking System...")
    if not check_db_connection():
        raise RuntimeError("Database connection failed at startup!")
    init_db()
    print("Application startup complete")

    yield

    # Shutdown
    print("Shutting down Amendment Tracking System...")


app = FastAPI(
    title="Amendment Tracking System",
    description=(
        "Internal amendment tracking system for managing application updates, "
        "bug fixes, enhancements, and feature requests."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


# CORS configuration from environment
cors_origins_str = os.getenv("CORS_ORIGINS", "http://localhost:3000")
cors_origins = [origin.strip() for origin in cors_origins_str.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    """Root endpoint with API information."""
    return {
        "message": "Amendment Tracking System API",
        "version": "1.0.0",
        "docs": "/docs",
        "openapi": "/openapi.json",
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    db_status = check_db_connection()
    return {
        "status": "healthy" if db_status else "unhealthy",
        "database": "connected" if db_status else "disconnected",
    }
