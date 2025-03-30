import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Database Configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "googlemaps")
DB_USER = os.getenv("DB_USER", "reviewsuser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "reviewspass")

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") 