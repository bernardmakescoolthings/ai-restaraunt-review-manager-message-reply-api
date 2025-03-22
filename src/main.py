from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Message Response API",
    description="API for generating responses using OpenAI's GPT models",
    version="1.0.0"
)

# Initialize OpenAI client with optional API key
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None

class MessageRequest(BaseModel):
    profile: str
    message: str

class MessageResponse(BaseModel):
    response: str

@app.post("/get_message_response", response_model=MessageResponse)
async def get_message_response(request: MessageRequest):
    try:
        if not client:
            raise HTTPException(
                status_code=500,
                detail="OpenAI API key not configured. Please set OPENAI_API_KEY environment variable."
            )
            
        # Create the system message with the personality profile
        system_message = f"You are an AI assistant with the following personality profile: {request.profile}"
        
        # Make the API call to OpenAI
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": request.message}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        # Extract the response
        ai_response = response.choices[0].message.content
        
        return MessageResponse(response=ai_response)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Welcome to the Message Response API"} 