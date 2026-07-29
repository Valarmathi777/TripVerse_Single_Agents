"""GET /weather - live weather for a destination via Open-Meteo (free, no API key)."""
from fastapi import APIRouter, HTTPException, Query
import httpx

from config import settings

router = APIRouter(tags=["Weather"])


@router.get("/weather")
def get_weather(destination: str = Query(..., description="City name, e.g. Ooty")):
    try:
        with httpx.Client(timeout=15.0) as client:
            geo_resp = client.get(settings.OPEN_METEO_GEOCODE_URL, params={
                "name": destination, "count": 1,
            })
            geo_resp.raise_for_status()
            results = geo_resp.json().get("results")
            if not results:
                raise HTTPException(status_code=404, detail=f"Could not locate '{destination}'")

            place = results[0]
            lat, lon = place["latitude"], place["longitude"]

            weather_resp = client.get(settings.OPEN_METEO_BASE_URL, params={
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,precipitation,weather_code,wind_speed_10m",
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max",
                "timezone": "auto",
            })
            weather_resp.raise_for_status()
            weather_data = weather_resp.json()

        return {
            "destination": destination,
            "resolved_location": {
                "name": place.get("name"),
                "country": place.get("country"),
                "latitude": lat,
                "longitude": lon,
            },
            "current": weather_data.get("current"),
            "daily_forecast": weather_data.get("daily"),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Weather service unavailable: {e}")
