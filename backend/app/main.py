"""
TruthLens FastAPI Backend - Main Application
Entry point for the fake news detection API
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager

from app.config import get_settings
from app.routes import detection
from app.middleware.error_handler import (
    validation_exception_handler,
    general_exception_handler
)
from app.utils.logger import setup_logger

settings = get_settings()
logger = setup_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for startup and shutdown
    """
    # Startup
    logger.info("="*70)
    logger.info("🚀 TruthLens Backend Starting...")
    logger.info("="*70)
    logger.info(f"App: {settings.APP_NAME}")
    logger.info(f"Version: {settings.APP_VERSION}")
    logger.info(f"Environment: {'DEBUG' if settings.DEBUG else 'PRODUCTION'}")
    logger.info(f"Model Path: {settings.MODEL_PATH}")
    logger.info("="*70)
    
    try:
        # Model will be loaded on first request (lazy loading)
        logger.info("✅ Backend initialization complete")
        logger.info("Model will be loaded on first request")
    except Exception as e:
        logger.error(f"❌ Initialization failed: {str(e)}", exc_info=True)
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 TruthLens Backend Shutting Down...")
    logger.info("✅ Cleanup complete")


# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    TruthLens Fake News Detection API
    
    ## Features
    - 99.3% accurate RoBERTa-based fake news detection
    - SHAP-based explainability (XAI)
    - Gemini LLM-generated human-readable explanations
    - DynamoDB prediction logging
    - Comprehensive error handling
    
    ## Endpoints
    - `POST /api/detect` - Detect fake news from title and text
    - `GET /api/health` - Health check
    
    ## Usage
    Send POST request to /api/detect with:
    ```
    {
        "title": "Article title here",
        "text": "Article content here..."
    }
    ```
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    debug=settings.DEBUG
)

# CORS Middleware - ALLOW ALL FOR LOCAL DEVELOPMENT
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)



# Exception Handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include Routers
app.include_router(detection.router)


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - API information
    """
    return {
        "message": "TruthLens Fake News Detection API",
        "version": settings.APP_VERSION,
        "status": "operational",
        "docs": "/docs",
        "endpoints": {
            "detect": "POST /api/detect",
            "health": "GET /api/health"
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting server on {settings.HOST}:{settings.PORT}")
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
