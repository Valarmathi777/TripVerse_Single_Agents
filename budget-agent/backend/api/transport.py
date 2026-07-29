"""GET /transport - local transport options for a destination, optionally enriched
with real routing/duration data from OpenRouteService when ORS_API_KEY is configured."""
from fastapi import APIRouter, HTTPException, Query
import httpx

from config import settings
from utils.helpers import load_csv
from services.gemini_dataset import ensure_destination_data
router = APIRouter(tags=["Transport"])


@router.get("/transport")
def get_transport(destination: str = Query(..., description="e.g. Ooty, Goa, Jaipur")):
    ensure_destination_data(destination)
    df = load_csv("fuel.csv")
    subset = df[df["destination"].str.lower() == destination.lower()]
    if subset.empty:
        raise HTTPException(status_code=404, detail=f"No transport data found for '{destination}'")

    return {
        "destination": destination,
        "source": "dataset",
        "transport_options": subset.to_dict(orient="records"),
        "ors_enabled": settings.ORS_ENABLED,
        "note": None if settings.ORS_ENABLED else (
            "Add ORS_API_KEY in .env to enable live route distance/duration lookups "
            "via OpenRouteService (openrouteservice.org - free tier available)."
        ),
    }


@router.get("/transport/route")
def get_route(
    start_lat: float, start_lon: float, end_lat: float, end_lon: float,
    profile: str = "driving-car",
):
    """Live routing via OpenRouteService - requires ORS_API_KEY."""
    if not settings.ORS_ENABLED:
        raise HTTPException(
            status_code=400,
            detail="ORS_API_KEY not configured. Add it to .env to use live routing.",
        )
    url = f"https://api.openrouteservice.org/v2/directions/{profile}"
    try:
        with httpx.Client(timeout=15.0) as client:
            resp = client.get(url, params={
                "api_key": settings.ORS_API_KEY,
                "start": f"{start_lon},{start_lat}",
                "end": f"{end_lon},{end_lat}",
            })
            resp.raise_for_status()
            data = resp.json()
        summary = data["features"][0]["properties"]["summary"]
        return {
            "distance_km": round(summary["distance"] / 1000, 2),
            "duration_minutes": round(summary["duration"] / 60, 1),
        }
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"OpenRouteService unavailable: {e}")
