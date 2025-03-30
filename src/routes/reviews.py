from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from datetime import datetime
import logging
import asyncpg

# Configure logging
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(
    prefix="/reviews",
    tags=["reviews"]
)

class BusinessReviewRequest(BaseModel):
    business_url: str

class Review(BaseModel):
    id: int
    id_review: str
    username: str
    rating: float
    timestamp: datetime
    review_text: str
    business_url: str
    n_review_user: int
    replies: str | None  # Added replies field, can be None if no reply exists

class BusinessReviewResponse(BaseModel):
    business_url: str
    reviews: list[Review]
    total_reviews: int
    average_rating: float

@router.post("/fetch", response_model=BusinessReviewResponse)
async def fetch_reviews(request: BusinessReviewRequest, req: Request):
    try:
        db_pool = req.app.state.db_pool
        if not db_pool:
            logger.error("Database connection pool not available")
            raise HTTPException(
                status_code=503,
                detail="Database service unavailable"
            )

        logger.info(f"Fetching reviews for business URL: {request.business_url}")
        try:
            async with db_pool.acquire() as connection:
                # Fetch reviews for the business
                reviews_query = """
                    SELECT 
                        id,
                        id_review,
                        username,
                        rating,
                        timestamp,
                        caption,
                        business_url,
                        n_review_user,
                        replies
                    FROM reviews
                    WHERE business_url = $1
                    ORDER BY timestamp DESC
                """
                
                # Get review statistics
                stats_query = """
                    SELECT 
                        COUNT(*) as total_reviews,
                        AVG(rating) as average_rating
                    FROM reviews
                    WHERE business_url = $1
                """
                
                # Execute both queries
                reviews = await connection.fetch(reviews_query, request.business_url)
                stats = await connection.fetchrow(stats_query, request.business_url)
                
                logger.info(f"Found {len(reviews)} reviews for the business")
                
                if not reviews:
                    return BusinessReviewResponse(
                        business_url=request.business_url,
                        reviews=[],
                        total_reviews=0,
                        average_rating=0.0
                    )
                
                # Convert the reviews to Pydantic models
                review_list = [
                    Review(
                        id=row['id'],
                        id_review=row['id_review'],
                        username=row['username'],
                        rating=float(row['rating']),
                        timestamp=row['timestamp'],
                        review_text=row['caption'] if row['caption'] is not None else "",
                        business_url=row['business_url'],
                        n_review_user=row['n_review_user'],
                        replies=row['replies']
                    )
                    for row in reviews
                ]
                
                return BusinessReviewResponse(
                    business_url=request.business_url,
                    reviews=review_list,
                    total_reviews=stats['total_reviews'],
                    average_rating=round(float(stats['average_rating']), 2) if stats['average_rating'] else 0.0
                )
                
        except asyncpg.PostgresError as e:
            logger.error(f"PostgreSQL error during query execution: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Database error: {str(e)}"
            )
            
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unexpected error in fetch_reviews: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        ) 