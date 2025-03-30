from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import message, reviews
from .database import init_db, close_db
from .config import API_BASE_URL
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Message Response API",
    description="API for generating responses using OpenAI's GPT models",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Store database pool and API base URL
app.state.db_pool = None
app.state.api_base_url = API_BASE_URL

# Include routers
app.include_router(message.router)
app.include_router(reviews.router)

@app.on_event("startup")
async def startup():
    logger.info("Starting application...")
    try:
        app.state.db_pool = await init_db()
        logger.info("Database initialized successfully")
        if app.state.db_pool:
            logger.info("Database pool is available")
        else:
            logger.error("Database pool is None after initialization")
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        raise

@app.on_event("shutdown")
async def shutdown():
    logger.info("Shutting down application...")
    await close_db()
    logger.info("Application shutdown complete")

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Message Response API",
        "api_base_url": app.state.api_base_url
    } 