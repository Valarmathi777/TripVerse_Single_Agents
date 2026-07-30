from typing import List, Dict, Any
from models.restaurant import UserPreference
from services.google_places_service import google_places_service
from restaurant_data import restaurants as fallback_dataset

class RestaurantRecommenderAgent:
    """Agent responsible for retrieving candidate restaurants from API or Dataset."""
    
    def find_restaurants(self, preference: UserPreference) -> List[Dict[str, Any]]:
        # Query Google Places API or fallback
        candidates = google_places_service.search_restaurants(
            location=preference.location,
            cuisine=preference.cuisine,
            food_preference=preference.food_preference,
            min_rating=preference.min_rating
        )

        if not candidates:
            candidates = fallback_dataset

        return candidates

restaurant_recommender_agent = RestaurantRecommenderAgent()
