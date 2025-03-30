import os
import asyncpg
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Database configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "user": os.getenv("DB_USER", "reviewsuser"),
    "password": os.getenv("DB_PASSWORD", "reviewspass"),
    "database": os.getenv("DB_NAME", "googlemaps"),
    "command_timeout": 60
}

# Database connection pool
db_pool = None

async def init_db():
    global db_pool
    try:
        # Log the configuration (excluding password)
        safe_config = {k: v for k, v in DB_CONFIG.items() if k != 'password'}
        logger.info(f"Initializing database connection pool with config: {safe_config}")
        
        # Try to create the pool
        pool = await asyncpg.create_pool(**DB_CONFIG)
        
        if not pool:
            raise Exception("Failed to create database pool")
            
        # Test the connection with a simple query
        async with pool.acquire() as conn:
            await conn.fetchval('SELECT 1')
            
        logger.info("Database connection pool created and tested successfully")
        db_pool = pool  # Assign the pool to the global variable
        return db_pool
        
    except asyncpg.PostgresError as e:
        logger.error(f"PostgreSQL error during connection: {str(e)}")
        db_pool = None  # Reset pool on error
        raise
    except Exception as e:
        logger.error(f"Failed to create database pool: {str(e)}")
        db_pool = None  # Reset pool on error
        raise

async def close_db():
    global db_pool
    if db_pool:
        await db_pool.close()
        db_pool = None  # Clear the pool reference
        logger.info("Database connection pool closed") 