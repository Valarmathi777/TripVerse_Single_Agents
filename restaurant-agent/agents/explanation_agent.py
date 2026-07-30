import json
from typing import List, Dict, Any
from models.restaurant import UserPreference
from services.gemini_service import gemini_service
from prompts import EXPLANATION_PROMPT
from utils import format_response

class ExplanationAgent:
    """Agent responsible for explaining why each restaurant is recommended using Gemini AI or fallback formatting."""
    
    def explain(self, restaurants: List[Dict[str, Any]], preference: UserPreference) -> str:
        if not restaurants:
            return "🍽 Restaurant Recommendations\n\nNo restaurants matched your criteria."

        enriched = self._enrich_restaurants(restaurants, preference)

        if gemini_service.client:
            try:
                prompt = self._build_prompt(enriched, preference)
                ai_explanation = gemini_service.generate_content(prompt)
                if ai_explanation and "🍽 Restaurant Recommendations" in ai_explanation:
                    return ai_explanation.strip()
            except Exception:
                pass

        return format_response(enriched, preference)

    async def explain_async(self, restaurants: List[Dict[str, Any]], preference: UserPreference) -> str:
        if not restaurants:
            return "🍽 Restaurant Recommendations\n\nNo restaurants matched your criteria."

        enriched = self._enrich_restaurants(restaurants, preference)

        if gemini_service.client:
            try:
                prompt = self._build_prompt(enriched, preference)
                ai_explanation = await gemini_service.generate_content_async(prompt)
                if ai_explanation and "🍽 Restaurant Recommendations" in ai_explanation:
                    return ai_explanation.strip()
            except Exception:
                pass

        return format_response(enriched, preference)

    def _enrich_restaurants(self, restaurants: List[Dict[str, Any]], preference: UserPreference) -> List[Dict[str, Any]]:
        enriched_restaurants = []
        for r in restaurants:
            r_copy = dict(r)
            reasons = []
            
            if preference.food_preference and preference.food_preference != "Any":
                reasons.append(f"Offers authentic {r.get('type', preference.food_preference)} options")
            else:
                reasons.append(f"Known for excellent {r.get('cuisine', 'local')} dishes")
                
            if preference.budget and preference.budget != "Any":
                reasons.append(f"Fits your {r.get('budget', preference.budget)} budget preference")
            else:
                reasons.append("Great value for quality food")
                
            reasons.append(f"Highly rated by diners with ⭐ {r.get('rating', 4.5)} rating")
            
            r_copy["reasons"] = reasons
            enriched_restaurants.append(r_copy)
        return enriched_restaurants

    def _build_prompt(self, enriched_restaurants: List[Dict[str, Any]], preference: UserPreference) -> str:
        restaurants_summary = json.dumps([
            {
                "name": r.get("name"),
                "rating": r.get("rating"),
                "cuisine": r.get("cuisine"),
                "budget": r.get("budget"),
                "type": r.get("type"),
                "meal_time": r.get("meal_time", "Lunch")
            } for r in enriched_restaurants[:5]
        ], indent=2)

        return EXPLANATION_PROMPT.format(
            location=preference.location,
            cuisine=preference.cuisine,
            budget=preference.budget,
            food_preference=preference.food_preference,
            min_rating=preference.min_rating,
            restaurants_json=restaurants_summary
        )

explanation_agent = ExplanationAgent()
