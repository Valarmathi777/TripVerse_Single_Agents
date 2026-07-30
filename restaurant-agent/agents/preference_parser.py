import re
from typing import Dict, Any, Union
from models.restaurant import UserPreference
from services.gemini_service import gemini_service
from prompts import PREFERENCE_PARSER_PROMPT
from utils import normalize_budget
from logger import logger

class PreferenceParserAgent:
    """Agentic AI component that parses unstructured user text into structured UserPreference."""
    
    def parse(self, user_input: Union[str, Dict[str, Any], UserPreference]) -> UserPreference:
        if isinstance(user_input, UserPreference):
            return user_input

        if isinstance(user_input, dict):
            return self._from_dict(user_input)

        query_str = str(user_input).strip()
        if not query_str:
            return UserPreference()

        # Try Gemini AI parser first
        prompt = PREFERENCE_PARSER_PROMPT.format(query=query_str)
        extracted = gemini_service.parse_json_response(prompt)
        if self._is_valid_extraction(extracted):
            return self._build_preference(extracted, query_str)

        # Fallback to Regex Heuristics
        return self._heuristic_parse(query_str)

    async def parse_async(self, user_input: Union[str, Dict[str, Any], UserPreference]) -> UserPreference:
        if isinstance(user_input, UserPreference):
            return user_input

        if isinstance(user_input, dict):
            return self._from_dict(user_input)

        query_str = str(user_input).strip()
        if not query_str:
            return UserPreference()

        # Try async Gemini AI parser
        prompt = PREFERENCE_PARSER_PROMPT.format(query=query_str)
        extracted = await gemini_service.parse_json_async(prompt)
        if self._is_valid_extraction(extracted):
            return self._build_preference(extracted, query_str)

        return self._heuristic_parse(query_str)

    def _from_dict(self, d: Dict[str, Any]) -> UserPreference:
        return UserPreference(
            location=d.get("location", "Tokyo") or "Tokyo",
            cuisine=d.get("cuisine", "Any") or "Any",
            budget=normalize_budget(d.get("budget", "Any")),
            food_preference=d.get("food_preference") or d.get("type", "Any") or "Any",
            min_rating=float(d.get("min_rating", 4.0)),
            meal_time=d.get("meal_time"),
            query=d.get("query")
        )

    def _is_valid_extraction(self, extracted: dict) -> bool:
        return bool(extracted and isinstance(extracted, dict) and ("location" in extracted or "food_preference" in extracted))

    def _build_preference(self, extracted: dict, query_str: str) -> UserPreference:
        return UserPreference(
            location=extracted.get("location", "Tokyo") or "Tokyo",
            cuisine=extracted.get("cuisine", "Any") or "Any",
            budget=normalize_budget(extracted.get("budget", "Any")),
            food_preference=extracted.get("food_preference", "Any") or "Any",
            min_rating=float(extracted.get("min_rating", 4.0)),
            meal_time=extracted.get("meal_time"),
            query=query_str
        )

    def _heuristic_parse(self, query_str: str) -> UserPreference:
        location = "Tokyo"
        budget = "Any"
        food_preference = "Any"
        cuisine = "Any"
        min_rating = 4.0

        lower = query_str.lower()

        if any(w in lower for w in ["cheap", "affordable", "low budget", "low", "inexpensive"]):
            budget = "Low"
        elif any(w in lower for w in ["moderate", "medium"]):
            budget = "Medium"
        elif any(w in lower for w in ["luxury", "expensive", "fine dining", "high"]):
            budget = "High"

        if "vegetarian" in lower or "veggie" in lower:
            food_preference = "Vegetarian"
        elif "vegan" in lower:
            food_preference = "Vegan"
        elif "halal" in lower:
            food_preference = "Halal"
        elif "non-vegetarian" in lower or "non veg" in lower:
            food_preference = "Non-Vegetarian"

        cuisines = ["japanese", "italian", "indian", "chinese", "mexican", "french", "american", "thai"]
        for c in cuisines:
            if c in lower:
                cuisine = c.capitalize()
                break

        locations = ["tokyo", "paris", "new york", "london", "kyoto", "osaka"]
        for loc in locations:
            if loc in lower:
                location = loc.capitalize()
                break

        rating_match = re.search(r'(\d(?:\.\d)?)\s*(?:star|⭐|\+|\b)', lower)
        if rating_match:
            try:
                min_rating = float(rating_match.group(1))
            except ValueError:
                pass

        return UserPreference(
            location=location,
            cuisine=cuisine,
            budget=budget,
            food_preference=food_preference,
            min_rating=min_rating,
            query=query_str
        )

preference_parser_agent = PreferenceParserAgent()
