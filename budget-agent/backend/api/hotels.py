"""GET /hotels - list hotels for a destination from the local dataset, optionally
enriched with live Geoapify place results when GEOAPIFY_API_KEY is configured."""
from fastapi import APIRouter, HTTPException, Query
import httpx
from services.gemini_dataset import ensure_destination_data
from config import settings
from utils.helpers import load_csv

router = APIRouter(tags=["Hotels"])


@router.get("/hotels")
def get_hotels(
    destination: str = Query(..., description="e.g. Ooty, Goa, Jaipur"),
    category: str | None = Query(None, description="Budget | Standard | Luxury"),
):
    ensure_destination_data(destination)
    df = load_csv("hotels.csv")
    subset = df[df["destination"].str.lower() == destination.lower()]
    if subset.empty:
        raise HTTPException(status_code=404, detail=f"No hotels found for '{destination}'")
    if category:
        subset = subset[subset["category"].str.lower() == category.lower()]

    hotels = subset.to_dict(orient="records")

    geoapify_places = []
    if settings.GEOAPIFY_ENABLED:
        try:
            geoapify_places = _fetch_geoapify_hotels(destination)
        except Exception as e:
            geoapify_places = []  # dataset result still returned even if live call fails

    return {
        "destination": destination,
        "source": "dataset",
        "hotels": hotels,
        "live_geoapify_results": geoapify_places,
        "geoapify_enabled": settings.GEOAPIFY_ENABLED,
    }


def _fetch_geoapify_hotels(destination: str):
    """Live enrichment: look up real accommodation places near the destination."""
    geocode_url = "https://api.geoapify.com/v1/geocode/search"
    with httpx.Client(timeout=15.0) as client:
        geo_resp = client.get(geocode_url, params={
            "text": destination, "apiKey": settings.GEOAPIFY_API_KEY, "limit": 1,
        })
        geo_resp.raise_for_status()
        features = geo_resp.json().get("features", [])
        if not features:
            return []
        lon, lat = features[0]["geometry"]["coordinates"]

        places_url = "https://api.geoapify.com/v2/places"
        places_resp = client.get(places_url, params={
            "categories": "accommodation.hotel",
            "filter": f"circle:{lon},{lat},8000",
            "bias": f"proximity:{lon},{lat}",
            "limit": 10,
            "apiKey": settings.GEOAPIFY_API_KEY,
        })
        places_resp.raise_for_status()
        data = places_resp.json().get("features", [])
        return [
            {
                "name": f["properties"].get("name", "Unnamed"),
                "address": f["properties"].get("formatted"),
                "lat": f["properties"].get("lat"),
                "lon": f["properties"].get("lon"),
            }
            for f in data
        ]
