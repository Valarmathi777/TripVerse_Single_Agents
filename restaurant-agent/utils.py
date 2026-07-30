import math
from typing import List, Dict, Any

def sort_by_rating(restaurants: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Sorts a list of restaurant dictionaries by rating descending."""
    return sorted(restaurants, key=lambda x: x.get("rating", 0.0), reverse=True)

def remove_duplicates(restaurants: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Removes duplicate restaurants based on lowercased name."""
    seen = set()
    unique = []
    for r in restaurants:
        name = r.get("name", "").strip().lower()
        if name and name not in seen:
            seen.add(name)
            unique.append(r)
    return unique

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates Haversine distance in kilometers between two geographic points."""
    R = 6371.0  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)

def normalize_budget(budget: str) -> str:
    """Normalizes budget text to Low, Medium, High, or Any."""
    if not budget:
        return "Any"
    b = budget.strip().lower()
    if "cheap" in b or "low" in b or "$" == b or "budget" in b:
        return "Low"
    elif "moderate" in b or "medium" in b or "$$" in b:
        return "Medium"
    elif "expensive" in b or "high" in b or "$$$" in b or "luxury" in b:
        return "High"
    return "Any"

def format_response(recommendations: List[Dict[str, Any]], preferences: Any = None) -> str:
    """Formats recommendations into standard Morning, Lunch, Dinner readable output format."""
    if not recommendations:
        return "🍽 Restaurant Recommendations\n\nNo matching restaurants found for your criteria. Try relaxing your filters!"

    mornings = [r for r in recommendations if r.get("meal_time", "").lower() == "morning"]
    lunches = [r for r in recommendations if r.get("meal_time", "").lower() == "lunch"]
    dinners = [r for r in recommendations if r.get("meal_time", "").lower() == "dinner"]

    # Fallback assignment if meal_time is unassigned
    unassigned = [r for r in recommendations if r.get("meal_time", "").lower() not in ["morning", "lunch", "dinner"]]
    for i, r in enumerate(unassigned):
        if i % 3 == 0 and not mornings:
            mornings.append(r)
        elif i % 3 == 1 and not lunches:
            lunches.append(r)
        else:
            dinners.append(r)

    if not mornings and not lunches and not dinners:
        # Divide arbitrarily
        for i, r in enumerate(recommendations):
            if i == 0:
                mornings.append(r)
            elif i == 1:
                lunches.append(r)
            else:
                dinners.append(r)

    lines = ["🍽 Restaurant Recommendations", ""]

    if mornings:
        lines.append("☕ Morning")
        for r in mornings:
            lines.append(f"• {r.get('name')} ⭐ {r.get('rating', 0.0)}")
            reasons = r.get("reasons") or [
                f"Cuisine: {r.get('cuisine')}",
                f"Dietary: {r.get('type')}",
                f"Fits your {r.get('budget', 'Medium')} budget"
            ]
            lines.append("  Reason:")
            for reason in reasons:
                lines.append(f"  • {reason}")
            lines.append("")

    if lunches:
        lines.append("🍣 Lunch")
        for r in lunches:
            lines.append(f"• {r.get('name')} ⭐ {r.get('rating', 0.0)}")
            reasons = r.get("reasons") or [
                f"Cuisine: {r.get('cuisine')}",
                f"Dietary: {r.get('type')}",
                f"Fits your {r.get('budget', 'Medium')} budget"
            ]
            lines.append("  Reason:")
            for reason in reasons:
                lines.append(f"  • {reason}")
            lines.append("")

    if dinners:
        lines.append("🍜 Dinner")
        for r in dinners:
            lines.append(f"• {r.get('name')} ⭐ {r.get('rating', 0.0)}")
            reasons = r.get("reasons") or [
                f"Cuisine: {r.get('cuisine')}",
                f"Dietary: {r.get('type')}",
                f"Fits your {r.get('budget', 'Medium')} budget"
            ]
            lines.append("  Reason:")
            for reason in reasons:
                lines.append(f"  • {reason}")
            lines.append("")

    return "\n".join(lines).strip()
