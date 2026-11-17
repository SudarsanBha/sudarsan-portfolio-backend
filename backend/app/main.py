import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.projects import router as projects_router
from app.routes.contact import router as contact_router
from app.routes.auth import router as auth_router
from app.routes.admin import router as admin_router

from app.config import settings
from app.schemas.health import HealthResponse

"""
from app.database import Base, engine
from app.models.users import User
from app.models.projects import Project
from app.models.contact import ContactMessage as ContactMessageModel
"""

# Application-wide logging configuration
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)

# FastAPI application configuration
app = FastAPI(
    title= settings.app_name,
    debug= settings.debug,
    version= settings.app_version,
    description= "Backend API for my developer Portfolio",
)

# Load allowed frontend origins from environment settings
allowed_origins = [
    origin.strip() for origin in
    settings.frontend_origin.split(",")
    if origin.strip()
]

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# Reggister Every Routes
app.include_router(projects_router)
app.include_router(contact_router)
app.include_router(auth_router)
app.include_router(admin_router)


# Create the database tables for the currently regestered models.
# Base.metadata.create_all(bind=engine)

# Root Endpoint
@app.get("/")
def home():
    return {
        "message": "Welcome to Sudarsan's portofolio",
           "status": "running"
    }


# Health Check endpoint
@app.get("/api/health", response_model=HealthResponse)
def health_check():
    return {
        "status": "healthy",
        "service": "portofolio-backend"
    }