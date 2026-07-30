import httpx
import requests
from typing import List, Dict, Any
from config import config
from logger import logger
from restaurant_data import restaurants as fallback_dataset

class GooglePlacesService:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or config.GOOGLE_PLACES_API_KEY

    def search_restaurants(
        self,
        location: str,
        cuisine: str = "Any",
        food_preference: str = "Any",
        min_rating: float = 4.0
    ) -> List[Dict[str, Any]]:
        """Synchronously searches for restaurants matching criteria."""
        if self.api_key:
            try:
                query_parts = [food_preference, cuisine, "restaurant", "in", location]
                query = " ".join([p for p in query_parts if p and p != "Any"])
                
                url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
                params = {"query": query, "key": self.api_key}
                res = requests.get(url, params=params, timeout=5)
                if res.status_code == 200:
                    data = res.json()
                    results = data.get("results", [])
                    if results:
                        return self._format_places_results(results, location, cuisine, food_preference, min_rating)
            except Exception as e:
                logger.warning(f"Google Places API request failed: {e}. Falling back to dataset.")

        return fallback_dataset

    async def search_restaurants_async(
        self,
        location: str,
        cuisine: str = "Any",
        food_preference: str = "Any",
        min_rating: float = 4.0
    ) -> List[Dict[str, Any]]:
        """Asynchronously searches for restaurants matching criteria using httpx."""
        if self.api_key:
            try:
                query_parts = [food_preference, cuisine, "restaurant", "in", location]
                query = " ".join([p for p in query_parts if p and p != "Any"])
                
                url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
                params = {"query": query, "key": self.api_key}
                
                async with httpx.AsyncClient(timeout=5.0) as client:
                    res = await client.get(url, params=params)
                    if res.status_code == 200:
                        data = res.json()
                        results = data.get("results", [])
                        if results:
                            return self._format_places_results(results, location, cuisine, food_preference, min_rating)
            except Exception as e:
                logger.warning(f"Async Google Places API request failed: {e}. Falling back to dataset.")

        return fallback_dataset

    def _format_places_results(self, results, location, cuisine, food_preference, min_rating):
        formatted = []
        for item in results:
            rating = float(item.get("rating", 4.0))
            if rating < min_rating:
                continue
            price_level = item.get("price_level", 2)
            budget = "Low" if price_level <= 1 else ("Medium" if price_level == 2 else "High")
            
            formatted.append({
                "name": item.get("name"),
                "location": location,
                "cuisine": cuisine if cuisine != "Any" else "Local",
                "budget": budget,
                "type": food_preference if food_preference != "Any" else "General",
                "rating": rating,
                "address": item.get("formatted_address"),
                "meal_time": "Lunch"
            })
        return formatted if formatted else fallback_dataset

google_places_service = GooglePlacesService()
