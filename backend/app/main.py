"""
Main FastAPI application entry point.
Configures middleware, CORS, routers, and application lifecycle events.
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import logging

from app.core.config import settings
from app.database.connection import init_db

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    docs_url="/api/docs" if settings.is_development else None,
    redoc_url="/api/redoc" if settings.is_development else None,
)


# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Trusted Host Middleware (security)
if settings.is_production:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["tutorlyplatform.com", "*.tutorlyplatform.com"],
    )


@app.on_event("startup")
async def startup_event():
    """
    Application startup event.
    Initialize database and other services.
    """
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")

    # Initialize database (create tables)
    # Note: In production, use Alembic migrations instead
    if settings.is_development:
        logger.info("Initializing database...")
        try:
            init_db()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event."""
    logger.info(f"Shutting down {settings.APP_NAME}")


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - health check."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "status": "running",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring."""
    return JSONResponse(
        content={
            "status": "healthy",
            "environment": settings.ENVIRONMENT,
            "version": settings.APP_VERSION,
        },
        status_code=200,
    )


# Mount static files directory for serving uploaded files
uploads_dir = os.path.join(os.getcwd(), "uploads")
if not os.path.exists(uploads_dir):
    os.makedirs(uploads_dir)
    logger.info(f"Created uploads directory: {uploads_dir}")

app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")
logger.info("Mounted static files directory: /uploads")

# Mount storage uploads directory (where actual uploads are stored)
storage_uploads_dir = os.path.join(os.getcwd(), "storage", "uploads")
if os.path.exists(storage_uploads_dir):
    app.mount("/storage/uploads", StaticFiles(directory=storage_uploads_dir), name="storage_uploads")
    logger.info(f"Mounted storage uploads directory: /storage/uploads -> {storage_uploads_dir}")


# Include routers
from app.routers import auth, instructor, upload, calendar

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(instructor.router, prefix="/api/instructor", tags=["Instructor"])
app.include_router(upload.router, prefix="/api/upload", tags=["File Upload"])
app.include_router(calendar.router, prefix="/api/calendar", tags=["Calendar & Scheduling"])

# Additional routers to be added as features are implemented:
# from app.routers import student, search, booking, session, messaging, payment, admin
# app.include_router(student.router, prefix="/api/student", tags=["Student"])
# app.include_router(search.router, prefix="/api/search", tags=["Search"])
# app.include_router(booking.router, prefix="/api/booking", tags=["Booking"])
# app.include_router(session.router, prefix="/api/session", tags=["Session"])
# app.include_router(messaging.router, prefix="/api/messaging", tags=["Messaging"])
# app.include_router(payment.router, prefix="/api/payment", tags=["Payment"])
# app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.is_development,
        log_level=settings.LOG_LEVEL.lower(),
    )
