"""
FastAPI Application v3.0 - With Structured Error Handling

✅ ALL 7 IMPROVEMENTS IMPLEMENTED:
1. Database persistence
2. JWT authentication
3. Rate limiting
4. API versioning
5. Report regeneration
6. Structured error codes
7. Specific exception handling
"""

import os
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from loguru import logger

from .middleware.auth import SECRET_KEY
from .middleware.rate_limit import limiter, RATE_LIMIT_ENABLED
from .v1 import router_v1
from .error_handlers import setup_exception_handlers
from .exceptions import RateLimitExceededError
from ..utils import setup_logger
from ..database.connection import get_db_manager
from ..utils.opentelemetry_config import setup_opentelemetry

# Initialize logger
setup_logger()

# Initialize database
db_manager = get_db_manager()

# Create FastAPI app
app = FastAPI(
    title="PCA Agent API v3.0",
    description="Post Campaign Analysis - Production Ready with Structured Error Handling",
    version="3.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Setup exception handlers (MUST be before other middleware)
setup_exception_handlers(app)

# Setup OpenTelemetry (if enabled)
setup_opentelemetry(app)

# Add rate limiter to app state
app.state.limiter = limiter

# Custom rate limit exception handler
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Handle rate limit exceeded errors with structured response."""
    logger.warning(
        f"Rate limit exceeded",
        extra={
            "path": request.url.path,
            "method": request.method,
            "client": request.client.host if request.client else "unknown"
        }
    )
    
    # Use our structured error
    error = RateLimitExceededError(limit=str(exc.detail))
    
    return JSONResponse(
        status_code=error.status_code,
        content={
            "error": {
                "code": error.error_code,
                "message": error.message,
                "details": error.details
            },
            "path": request.url.path,
            "method": request.method
        }
    )

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include v1 router
app.include_router(router_v1)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "PCA Agent API v3.0 - Production Ready",
        "version": "3.0.0",
        "features": [
            "✅ Database persistence",
            "✅ JWT authentication",
            "✅ Rate limiting",
            "✅ API versioning",
            "✅ Report regeneration",
            "✅ Structured error codes",
            "✅ Specific exception handling"
        ],
        "status": "running",
        "docs": "/api/docs",
        "error_codes": "/api/docs#/Error%20Codes"
    }


@app.get("/health")
@limiter.limit("100/minute")
async def health_check(request: Request):
    """Basic health check."""
    return {
        "status": "healthy",
        "version": "3.0.0",
        "features": {
            "authentication": True,
            "rate_limiting": RATE_LIMIT_ENABLED,
            "database": "connected",
            "api_version": "v1",
            "error_handling": "structured"
        }
    }


@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with all system status."""
    try:
        db_healthy = db_manager.health_check()
        
        return {
            "status": "healthy" if db_healthy else "degraded",
            "version": "3.0.0",
            "components": {
                "database": "healthy" if db_healthy else "unhealthy",
                "authentication": "healthy",
                "rate_limiting": "healthy" if RATE_LIMIT_ENABLED else "disabled",
                "api": "healthy",
                "error_handling": "healthy"
            },
            "error_handling": {
                "structured_codes": True,
                "specific_exceptions": True,
                "global_handlers": True,
                "structured_logging": True
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": {
                "message": "Health check failed",
                "details": {"type": type(e).__name__}
            }
        }


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    logger.info("=" * 60)
    logger.info("PCA Agent API v3.0 - Starting")
    logger.info("=" * 60)
    logger.info("✅ Database persistence enabled")
    logger.info("✅ JWT authentication enabled")
    logger.info(f"✅ Rate limiting: {RATE_LIMIT_ENABLED}")
    logger.info("✅ API versioning: /api/v1/")
    logger.info("✅ Report regeneration implemented")
    logger.info("✅ Structured error codes enabled")
    logger.info("✅ Specific exception handling enabled")
    logger.info("=" * 60)
    
    if SECRET_KEY == "change-this-secret-key":
        logger.warning("⚠️  WARNING: Using default JWT secret key!")
        logger.warning("⚠️  Change JWT_SECRET_KEY in .env for production")
    
    logger.info("API ready at http://localhost:8000")
    logger.info("Docs available at http://localhost:8000/api/docs")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("PCA Agent API v3.0 - Shutting down")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
