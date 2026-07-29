"""
Central configuration for the Budget Agent backend.
All secrets are loaded from environment variables (see .env at the project root).
Nothing here should ever hardcode a real key - only safe fallbacks/placeholders.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root (one level up from backend/)
BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
load_dotenv(ROOT_DIR / ".env")


class Settings:
    # --- App ---
    APP_NAME: str = "Budget Agent"
    ENV: str = os.getenv("ENV", "development")
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

    # --- Gemini (Google AI Studio) ---
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
    GEMINI_ENABLED: bool = bool(GEMINI_API_KEY)

    # --- Geoapify (places / hotel geocoding enrichment) ---
    GEOAPIFY_API_KEY: str = os.getenv("GEOAPIFY_API_KEY", "")
    GEOAPIFY_ENABLED: bool = bool(GEOAPIFY_API_KEY)

    # --- OpenRouteService (transport distance/duration) ---
    ORS_API_KEY: str = os.getenv("ORS_API_KEY", "")
    ORS_ENABLED: bool = bool(ORS_API_KEY)

    # --- Open-Meteo (weather) - no key required ---
    OPEN_METEO_BASE_URL: str = "https://api.open-meteo.com/v1/forecast"
    OPEN_METEO_GEOCODE_URL: str = "https://geocoding-api.open-meteo.com/v1/search"

    # --- Frankfurter (currency conversion) - no key required ---
    FRANKFURTER_BASE_URL: str = "https://api.frankfurter.dev/v1/latest"

    # --- Database (PostgreSQL) ---
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://budget_user:budget_pass@localhost:5432/budget_agent",
    )

    # --- Paths ---
    DATASETS_DIR: Path = BASE_DIR / "datasets"
    MODELS_DIR: Path = BASE_DIR / "models"
    PROMPTS_DIR: Path = BASE_DIR / "prompts"


settings = Settings()
