"""GET /restaurants - list restaurants/food options for a destination from the local dataset."""
from fastapi import APIRouter, HTTPException, Query

from utils.helpers import load_csv
from services.gemini_dataset import ensure_destination_data
router = APIRouter(tags=["Restaurants"])


@router.get("/restaurants")
def get_restaurants(
    destination: str = Query(..., description="e.g. Ooty, Goa, Jaipur"),
    category: str | None = Query(None, description="Budget | Standard | Luxury"),
):
    ensure_destination_data(destination)
    df = load_csv("restaurants.csv")
    subset = df[df["destination"].str.lower() == destination.lower()]
    if subset.empty:
        raise HTTPException(status_code=404, detail=f"No restaurants found for '{destination}'")
    if category:
        subset = subset[subset["category"].str.lower() == category.lower()]

    return {
        "destination": destination,
        "restaurants": subset.to_dict(orient="records"),
    }
