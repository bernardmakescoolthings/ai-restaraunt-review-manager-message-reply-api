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
    business_place_id: str

class Review(BaseModel):
    id: int
    review_id: str
    username: str
    rating: float
    timestamp: datetime | None
    review_text: str
    business_place_id: str
    n_review_user: int
    replies: str | None
    review_timestamp: int | None
    url_user: str | None

class BusinessReviewResponse(BaseModel):
    business_place_id: str
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

        logger.info(f"Fetching reviews for business place ID: {request.business_place_id}")
        try:
            async with db_pool.acquire() as connection:
                # Fetch reviews for the business
                reviews_query = """
                    SELECT 
                        id,
                        review_id,
                        author_title as username,
                        review_rating as rating,
                        review_datetime_utc as timestamp,
                        review_text,
                        business_place_id,
                        author_reviews_count as n_review_user,
                        replies,
                        review_timestamp,
                        author_link as url_user
                    FROM reviews
                    WHERE business_place_id = $1
                    ORDER BY review_datetime_utc DESC
                """
                
                # Get review statistics
                stats_query = """
                    SELECT 
                        COUNT(*) as total_reviews,
                        AVG(review_rating) as average_rating
                    FROM reviews
                    WHERE business_place_id = $1
                """
                
                # Execute both queries
                reviews = await connection.fetch(reviews_query, request.business_place_id)
                stats = await connection.fetchrow(stats_query, request.business_place_id)
                
                logger.info(f"Found {len(reviews)} reviews for the business")
                
                if not reviews:
                    return BusinessReviewResponse(
                        business_place_id=request.business_place_id,
                        reviews=[],
                        total_reviews=0,
                        average_rating=0.0
                    )
                
                # Convert the reviews to Pydantic models
                review_list = [
                    Review(
                        id=row['id'],
                        review_id=row['review_id'],
                        username=row['username'],
                        rating=float(row['rating']),
                        timestamp=row['timestamp'],
                        review_text=row['review_text'] if row['review_text'] is not None else "",
                        business_place_id=row['business_place_id'],
                        n_review_user=row['n_review_user'],
                        replies=row['replies'],
                        review_timestamp=row['review_timestamp'],
                        url_user=row['url_user']
                    )
                    for row in reviews
                ]
                
                return BusinessReviewResponse(
                    business_place_id=request.business_place_id,
                    reviews=review_list,
                    total_reviews=stats['total_reviews'],
                    average_rating=float(stats['average_rating']) if stats['average_rating'] is not None else 0.0
                )
                
        except asyncpg.PostgresError as e:
            logger.error(f"Database error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Database error occurred"
            )
            
    except Exception as e:
        logger.error(f"Error fetching reviews: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        ) 