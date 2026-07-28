import requests
from config import OPENWEATHER_API_KEY, OPENWEATHER_URL

def get_weather(lat: float, lon: float) -> dict:
    try:
        resp = requests.get(OPENWEATHER_URL, params={
            "lat": lat, "lon": lon,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric"
        }, timeout=10)
        data = resp.json()
        if resp.status_code == 200:
            return {
                "condition": data["weather"][0]["main"],
                "description": data["weather"][0]["description"],
                "temp": data["main"]["temp"],
                "icon": data["weather"][0]["icon"]
            }
    except Exception:
        pass
    return {"condition": "Unknown", "description": "N/A", "temp": None, "icon": "01d"}

def weather_blocks_transport(weather: dict, mode: str) -> bool:
    condition = weather.get("condition", "").lower()
    if condition in ["thunderstorm", "tornado"]:
        return True
    if condition in ["snow", "blizzard"] and mode in ["bike", "walking"]:
        return True
    return False
