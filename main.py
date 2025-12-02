"""
Crypto Portfolio Tracker - FastAPI Application
===============================================

Entry point for the FastAPI application with database initialization.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os

# Setup logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown"""
    logger.info("🚀 Crypto Portfolio Tracker starting...")
    
    # Startup
    try:
        from src.database import init_database, run_migrations
        from src.utils.logger_setup import setup_logging
        
        # Initialize logging
        log_file = os.getenv("LOG_FILE", "logs/app.log")
        setup_logging(log_file=log_file)
        
        # Initialize database
        init_database()
        
        # Run migrations
        run_migrations()
        
        logger.info("✅ Application startup completed")
    except Exception as e:
        logger.error(f"❌ Startup error: {str(e)}", exc_info=True)
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Crypto Portfolio Tracker shutting down...")
    try:
        from src.database.manager import get_db_manager
        db = get_db_manager()
        db.close()
        logger.info("✅ Database connections closed")
    except Exception as e:
        logger.error(f"Shutdown error: {str(e)}")


# Create FastAPI app
app = FastAPI(
    title="Crypto Portfolio Tracker",
    description="Advanced cryptocurrency portfolio management and tax calculation",
    version="3.0.0",
    lifespan=lifespan,
)


from src.api.v1.routes import router as v1_router

# Include API routes
app.include_router(v1_router)

# OpenAPI documentation
@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    """Redirect to API docs"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/docs")


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Crypto Portfolio Tracker API",
        "version": "3.0.0",
        "status": "running",
    }


@app.get("/health")
async def health():
    """Health check"""
    from src.database.manager import get_db_manager
    db = get_db_manager()
    
    if db.health_check():
        return {"status": "ok", "database": "connected"}
    return {"status": "degraded", "database": "disconnected"}


@app.get("/health/live")
async def health_live():
    """Liveness probe"""
    return {"status": "alive"}


@app.get("/health/ready")
async def health_ready():
    """Readiness probe"""
    from src.database.manager import get_db_manager
    db = get_db_manager()
    
    if db.health_check():
        return {"status": "ready"}
    return {"status": "not_ready"}, 503


@app.get("/info")
async def info():
    """API info"""
    return {
        "name": "Crypto Portfolio Tracker",
        "version": "3.0.0",
        "status": "beta",
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health",
        },
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
