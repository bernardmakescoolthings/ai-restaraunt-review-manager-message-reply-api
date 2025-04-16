from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from openai import OpenAI
import os
from dotenv import load_dotenv
import logging
import asyncpg

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize router
router = APIRouter(
    prefix="/message",
    tags=["message"]
)

# Initialize OpenAI client with optional API key
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None

class MessageRequest(BaseModel):
    profile_id: int
    message_id: str

class MessageResponse(BaseModel):
    response: str

@router.post("/get_response", response_model=MessageResponse)
async def get_message_response(request: MessageRequest, req: Request):
    try:
        if not client:
            raise HTTPException(
                status_code=500,
                detail="OpenAI API key not configured. Please set OPENAI_API_KEY environment variable."
            )

        # Get database pool
        db_pool = req.app.state.db_pool
        if not db_pool:
            logger.error("Database connection pool not available")
            raise HTTPException(
                status_code=503,
                detail="Database service unavailable"
            )

        # Fetch profile and message from database
        try:
            async with db_pool.acquire() as connection:
                # First fetch the profile
                profile_query = """
                    SELECT profile_text_base, profile_text_addon
                    FROM profiles
                    WHERE id = $1
                """
                profile_row = await connection.fetchrow(profile_query, request.profile_id)
                
                if not profile_row:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Profile with ID {request.profile_id} not found"
                    )
                
                # Combine profile texts with a newline
                profile_text = f"{profile_row['profile_text_base']}\n{profile_row['profile_text_addon']}"
                
                # Then fetch the message, username, and rating
                message_query = """
                    SELECT review_text as message, author_title as username, review_rating as rating
                    FROM reviews
                    WHERE review_id = $1
                """
                message_row = await connection.fetchrow(message_query, request.message_id)
                
                if not message_row:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Review with ID {request.message_id} not found"
                    )
                
                message_content = f"{message_row['message']} - sent by {message_row['username'].split(' ')[0]} who gave a rating of {message_row['rating']} stars"
        except asyncpg.PostgresError as e:
            logger.error(f"Database error while fetching data: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Database error: {str(e)}"
            )
            
        # Create the system message with the personality profile
        system_message = f"You are an AI assistant with the following personality profile: {profile_text}"
        
        # Make the API call to OpenAI
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": message_content}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        # Extract the response
        ai_response = response.choices[0].message.content

        # Save the response to the database
        try:
            async with db_pool.acquire() as connection:
                update_query = """
                    UPDATE reviews
                    SET replies = $1
                    WHERE review_id = $2
                """
                await connection.execute(update_query, ai_response, request.message_id)
                logger.info(f"Successfully saved response for review {request.message_id}")
        except asyncpg.PostgresError as e:
            logger.error(f"Database error while saving response: {str(e)}")
            # Don't raise an error here as we still want to return the response to the user
        
        return MessageResponse(response=ai_response)
    
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unexpected error in get_message_response: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 