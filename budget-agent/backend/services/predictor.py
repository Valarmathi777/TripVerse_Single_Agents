"""
services/predictor.py
Two responsibilities:
  1. predict_quick_estimate() - loads models/budget_model.pkl (a RandomForest
     trained on the calculator engine's output) to return an instant rough
     total-cost estimate without recomputing all dataset lookups.
  2. generate_ai_recommendation() - calls Gemini (Google AI Studio) with the
     prompts/budget_prompt.txt template to produce the natural-language
     "AI Recommendation Panel" text shown on the dashboard.

If GEMINI_API_KEY is not configured, generate_ai_recommendation() falls back to
a clear, rule-based recommendation so the app still works end-to-end without a key.
"""
import functools
import json
from pathlib import Path

import joblib
import httpx

from config import settings
from utils.helpers import format_inr

_MODEL_PATH = settings.MODELS_DIR / "budget_model.pkl"


@functools.lru_cache(maxsize=1)
def _load_model():
    if not _MODEL_PATH.exists():
        return None
    return joblib.load(_MODEL_PATH)


def predict_quick_estimate(destination: str, days: int, travelers: int, travel_style: str) -> float:
    """Instant rough total-cost estimate using the trained regression model."""
    model = _load_model()
    if model is None:
        return None
    import pandas as pd
    try:
        X = pd.DataFrame([{
            "destination": destination,
            "days": days,
            "travelers": travelers,
            "travel_style": travel_style,
        }])
        prediction = model.predict(X)[0]
        return round(float(prediction), 2)
    except Exception:
        # Fallback heuristic calculation if destination is unknown to the ML model
        base_rate = {"Budget": 1800, "Standard": 4500, "Luxury": 12000}.get(travel_style, 4500)
        # Check if the destination is likely international
        known_domestic = ["ooty", "goa", "manali", "jaipur", "munnar", "coorg", "rishikesh", "pondicherry", "udaipur", "darjeeling"]
        is_intl = destination.lower().strip() not in known_domestic
        if is_intl:
            base_rate *= 1.8  # international scale factor
        estimated = base_rate * days * travelers
        return round(float(estimated), 2)

def _load_prompt_template() -> str:
    path = settings.PROMPTS_DIR / "budget_prompt.txt"
    return path.read_text()


def _rule_based_recommendation(destination, days, travelers, travel_style, breakdown, total_cost, budget) -> str:
    """Fallback used when no Gemini API key is configured."""
    diff = total_cost - budget
    if diff <= 0:
        return (
            f"Your {days}-day {travel_style.lower()} trip to {destination} for {travelers} traveler(s) "
            f"comes in at {format_inr(total_cost)}, which is within your {format_inr(budget)} budget with "
            f"{format_inr(abs(diff))} to spare. To stretch it further, consider a lower hotel category or "
            f"using local transport instead of private cabs."
        )
    biggest_category = max(breakdown, key=breakdown.get)
    return (
        f"Your trip to {destination} exceeds the budget by {format_inr(diff)}. The largest cost driver is "
        f"{biggest_category} at {format_inr(breakdown[biggest_category])}. Switching to a lower-cost option "
        f"in that category, along with using public transport and prioritizing free attractions, should bring "
        f"the trip back within budget while keeping a similar travel experience."
    )


def generate_ai_recommendation(destination, days, travelers, budget, travel_style, breakdown, total_cost) -> dict:
    """
    Returns {"text": str, "source": "gemini" | "rule_based"}
    """
    diff = round(total_cost - budget, 2)
    status = "over budget" if diff > 0 else "within budget"

    if not settings.GEMINI_ENABLED:
        return {
            "text": _rule_based_recommendation(
                destination, days, travelers, travel_style, breakdown, total_cost, budget
            ),
            "source": "rule_based",
            "note": "Add GEMINI_API_KEY in .env to enable AI-generated recommendations.",
        }

    template = _load_prompt_template()
    prompt = template.format(
        destination=destination,
        days=days,
        travelers=travelers,
        travel_style=travel_style,
        budget=f"{budget:,.0f}",
        breakdown=json.dumps({k: round(v) for k, v in breakdown.items()}),
        total_cost=f"{total_cost:,.0f}",
        difference=f"{abs(diff):,.0f}",
        status=status,
    )

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{settings.GEMINI_MODEL}:generateContent?key={settings.GEMINI_API_KEY}"
    )
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        with httpx.Client(timeout=20.0) as client:
            resp = client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            return {"text": text, "source": "gemini"}
    except Exception as e:
        # Never let an API hiccup break the dashboard - fall back gracefully.
        fallback = _rule_based_recommendation(
            destination, days, travelers, travel_style, breakdown, total_cost, budget
        )
        return {
            "text": fallback,
            "source": "rule_based",
            "note": f"Gemini call failed ({type(e).__name__}), showed rule-based fallback instead.",
        }
