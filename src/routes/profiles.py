from fastapi import APIRouter, HTTPException, Request
from typing import List, Dict
from pydantic import BaseModel
import logging
import asyncpg

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/profiles",
    tags=["profiles"]
)

class ProfileInput(BaseModel):
    profile_name: str
    profile_text_addon: str

class ProfileUpdateInput(BaseModel):
    profile_name: str | None = None
    profile_text_addon: str | None = None

class ProfileResponse(BaseModel):
    id: int
    profile_name: str
    profile_text_base: str
    profile_text_addon: str

class ProfileListResponse(BaseModel):
    id: int
    profile_name: str
    profile_text_addon: str

@router.get("/fetch_profiles", response_model=List[ProfileListResponse])
async def fetch_profiles(req: Request):
    """
    Fetch all profiles from the database.
    Returns a list of all profiles with their complete information.
    Note: profile_text_base is excluded from the response.
    """
    try:
        db_pool = req.app.state.db_pool
        if not db_pool:
            logger.error("Database connection pool not available")
            raise HTTPException(
                status_code=503,
                detail="Database service unavailable"
            )

        async with db_pool.acquire() as conn:
            profiles = await conn.fetch("""
                SELECT id, profile_name, profile_text_addon 
                FROM profiles
                ORDER BY id
            """)
            return [dict(profile) for profile in profiles]
    except Exception as e:
        logger.error(f"Error fetching profiles: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch profiles")

@router.post("/add_profiles", response_model=ProfileResponse)
async def add_profiles(profile: ProfileInput, req: Request):
    """
    Add a new profile to the database.
    Takes a profile object and inserts it into the profiles table.
    Sets profile_text_base to a default value.
    """
    try:
        db_pool = req.app.state.db_pool
        if not db_pool:
            logger.error("Database connection pool not available")
            raise HTTPException(
                status_code=503,
                detail="Database service unavailable"
            )

        # Set the profile_text_base value
        profile_text_base = "You are a friendly customer service representative known for your warm, empathetic approach. When replying to a negative review, keep your response brief (2–3 sentences). Acknowledge the customer's feelings, offer a sincere apology, and invite them to reach out for further assistance—all while maintaining a respectful, conversational tone."
        
        async with db_pool.acquire() as conn:
            profile_id = await conn.fetchval("""
                INSERT INTO profiles (profile_name, profile_text_base, profile_text_addon)
                VALUES ($1, $2, $3)
                RETURNING id
            """, profile.profile_name, profile_text_base, profile.profile_text_addon)
            
            # Fetch the newly created profile
            new_profile = await conn.fetchrow("""
                SELECT id, profile_name, profile_text_base, profile_text_addon
                FROM profiles
                WHERE id = $1
            """, profile_id)
            
            return dict(new_profile)
    except Exception as e:
        logger.error(f"Error adding profile: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to add profile")

@router.put("/update_profile/{profile_id}", response_model=ProfileResponse)
async def update_profile(profile_id: int, profile: ProfileUpdateInput, req: Request):
    """
    Update an existing profile in the database.
    Takes a profile ID and the fields to update.
    Returns the updated profile.
    Note: profile_text_base cannot be updated through this endpoint.
    """
    try:
        db_pool = req.app.state.db_pool
        if not db_pool:
            logger.error("Database connection pool not available")
            raise HTTPException(
                status_code=503,
                detail="Database service unavailable"
            )

        async with db_pool.acquire() as conn:
            # First check if the profile exists
            existing_profile = await conn.fetchrow("""
                SELECT id, profile_name, profile_text_base, profile_text_addon
                FROM profiles
                WHERE id = $1
            """, profile_id)
            
            if not existing_profile:
                raise HTTPException(
                    status_code=404,
                    detail=f"Profile with ID {profile_id} not found"
                )

            # Build the update query dynamically based on provided fields
            update_fields = []
            query_params = []
            param_count = 1

            if profile.profile_name is not None:
                update_fields.append(f"profile_name = ${param_count}")
                query_params.append(profile.profile_name)
                param_count += 1

            if profile.profile_text_addon is not None:
                update_fields.append(f"profile_text_addon = ${param_count}")
                query_params.append(profile.profile_text_addon)
                param_count += 1

            if not update_fields:
                raise HTTPException(
                    status_code=400,
                    detail="No fields provided for update"
                )

            # Add profile_id as the last parameter
            query_params.append(profile_id)
            
            # Construct and execute the update query
            update_query = f"""
                UPDATE profiles 
                SET {', '.join(update_fields)}
                WHERE id = ${param_count}
                RETURNING id, profile_name, profile_text_base, profile_text_addon
            """
            
            updated_profile = await conn.fetchrow(update_query, *query_params)
            
            if not updated_profile:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to update profile"
                )
            
            return dict(updated_profile)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating profile: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update profile")

@router.delete("/delete_profile/{profile_id}")
async def delete_profile(profile_id: int, req: Request):
    """
    Delete a profile from the database.
    Takes a profile ID and removes the corresponding profile.
    Returns a success message if the profile was deleted.
    """
    try:
        db_pool = req.app.state.db_pool
        if not db_pool:
            logger.error("Database connection pool not available")
            raise HTTPException(
                status_code=503,
                detail="Database service unavailable"
            )

        async with db_pool.acquire() as conn:
            # First check if the profile exists
            existing_profile = await conn.fetchrow("""
                SELECT id FROM profiles WHERE id = $1
            """, profile_id)
            
            if not existing_profile:
                raise HTTPException(
                    status_code=404,
                    detail=f"Profile with ID {profile_id} not found"
                )

            # Delete the profile
            await conn.execute("""
                DELETE FROM profiles WHERE id = $1
            """, profile_id)
            
            return {"message": f"Profile with ID {profile_id} was successfully deleted"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting profile: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete profile") 