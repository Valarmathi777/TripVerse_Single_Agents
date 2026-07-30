from typing import List, Dict, Any
from models.restaurant import UserPreference
from utils import remove_duplicates
from logger import logger

class RankingAgent:
    """
    Enterprise Ranking Agent implementing Multi-Attribute Utility Theory (MAUT) scoring matrix:
    - Dietary Type Match: 35% weight
    - Rating Score (Rating/5.0): 30% weight
    - Budget Level Match: 20% weight
    - Location & Cuisine Relevance: 15% weight
    """

    WEIGHT_DIET = 0.35
    WEIGHT_RATING = 0.30
    WEIGHT_BUDGET = 0.20
    WEIGHT_LOCATION_CUISINE = 0.15

    def rank(self, candidate_restaurants: List[Dict[str, Any]], preference: UserPreference) -> List[Dict[str, Any]]:
        if not candidate_restaurants:
            return []

        unique_candidates = remove_duplicates(candidate_restaurants)
        scored_restaurants = []

        target_loc = preference.location.strip().lower() if preference.location else "any"
        target_cuisine = preference.cuisine.strip().lower() if preference.cuisine else "any"
        target_budget = preference.budget.strip().lower() if preference.budget else "any"
        target_type = preference.food_preference.strip().lower() if preference.food_preference else "any"
        min_rating = preference.min_rating or 0.0

        for r in unique_candidates:
            rating = float(r.get("rating", 4.0))
            if rating < min_rating:
                continue

            r_loc = str(r.get("location", "")).strip().lower()
            r_cuisine = str(r.get("cuisine", "")).strip().lower()
            r_budget = str(r.get("budget", "")).strip().lower()
            r_type = str(r.get("type", "")).strip().lower()

            # 1. Dietary score (0.0 to 1.0)
            if target_type in ["any", ""] or target_type in r_type or r_type in target_type:
                diet_score = 1.0
            else:
                diet_score = 0.0

            # 2. Rating score (0.0 to 1.0)
            rating_score = min(1.0, max(0.0, rating / 5.0))

            # 3. Budget score (0.0 to 1.0)
            if target_budget in ["any", ""] or target_budget == r_budget:
                budget_score = 1.0
            else:
                budget_score = 0.5  # partial compatibility

            # 4. Location & Cuisine score (0.0 to 1.0)
            loc_match = (target_loc in ["any", ""] or target_loc in r_loc or r_loc in target_loc)
            cui_match = (target_cuisine in ["any", ""] or target_cuisine in r_cuisine)
            if loc_match and cui_match:
                loc_cui_score = 1.0
            elif loc_match or cui_match:
                loc_cui_score = 0.6
            else:
                loc_cui_score = 0.2

            # Weighted Utility Formula
            total_utility = (
                (diet_score * self.WEIGHT_DIET) +
                (rating_score * self.WEIGHT_RATING) +
                (budget_score * self.WEIGHT_BUDGET) +
                (loc_cui_score * self.WEIGHT_LOCATION_CUISINE)
            )

            final_score = round(total_utility * 100, 1)

            r_copy = dict(r)
            r_copy["match_score"] = final_score
            scored_restaurants.append(r_copy)

        # Sort by match_score descending, then rating descending
        ranked = sorted(scored_restaurants, key=lambda x: (x["match_score"], x.get("rating", 0.0)), reverse=True)
        return ranked

ranking_agent = RankingAgent()
