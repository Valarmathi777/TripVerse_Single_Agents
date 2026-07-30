import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GOOGLE_PLACES_API_KEY: str = os.getenv("GOOGLE_PLACES_API_KEY", "")
    DEFAULT_LOCATION: str = os.getenv("DEFAULT_LOCATION", "Tokyo")
    DEFAULT_MIN_RATING: float = float(os.getenv("DEFAULT_MIN_RATING", "4.0"))

config = Config()
