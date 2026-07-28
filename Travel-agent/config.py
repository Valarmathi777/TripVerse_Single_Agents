import os

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
OPENROUTE_API_KEY = os.getenv("OPENROUTE_API_KEY", "")
GEOAPIFY_API_KEY = os.getenv("GEOAPIFY_API_KEY", "your_geoapify_key")
AMADEUS_API_KEY = os.getenv("AMADEUS_API_KEY", "")
AMADEUS_API_SECRET = os.getenv("AMADEUS_API_SECRET", "")

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
OPENROUTE_URL = "https://api.openrouteservice.org/v2/directions"
OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"

PREFERENCE_WEIGHTS = {
    "fastest": {"time": 0.60, "cost": 0.15, "transfers": 0.15, "traffic": 0.10},
    "cheapest": {"time": 0.20, "cost": 0.60, "transfers": 0.20, "traffic": 0.00},
    "eco": {"time": 0.20, "cost": 0.20, "transfers": 0.20, "traffic": 0.10, "eco_bonus": 0.30},
    "comfort": {"time": 0.30, "cost": 0.20, "transfers": 0.30, "traffic": 0.20},
    "scenic": {"time": 0.20, "cost": 0.20, "transfers": 0.20, "traffic": 0.10, "scenic_bonus": 0.30},
}

ECO_MODES = ["walking", "bike", "metro", "train", "bus"]
TAXI_CAPACITY = 4
