"""
services/calculator.py
The Budget Calculation Engine.

Given a destination, number of days, travelers, and a travel style, this module
derives a full category-wise cost breakdown from the local CSV datasets:
    Hotel, Food, Transport, Attractions, Shopping, Emergency buffer

It also produces a day-by-day cost curve for the DailyExpenseChart.
"""
import random
from utils.helpers import load_csv, rooms_required

# Shopping is modeled as a percentage of the (hotel+food+transport+attractions)
# subtotal, scaled by travel style - there's no shopping.csv in the spec, so we
# derive it deterministically from style instead of hardcoding a flat rupee value.
SHOPPING_PCT = {"Budget": 0.05, "Standard": 0.08, "Luxury": 0.12}
EMERGENCY_PCT = 0.10

# Which hotel/transport/food dataset "category" values correspond to each style
STYLE_TO_CATEGORY = {
    "Budget": "Budget",
    "Standard": "Standard",
    "Luxury": "Luxury",
}

MEALS_PER_DAY = 3


def _avg_price(df, destination: str, category: str, column: str):
    subset = df[(df["destination"].str.lower() == destination.lower()) & (df["category"] == category)]
    if subset.empty:
        # fall back to any category for that destination rather than failing
        subset = df[df["destination"].str.lower() == destination.lower()]
    if subset.empty:
        raise ValueError(f"No dataset rows found for destination '{destination}'")
    return float(subset[column].mean())


def calculate_hotel_cost(destination: str, days: int, travelers: int, style: str):
    hotels = load_csv("hotels.csv")
    category = STYLE_TO_CATEGORY[style]
    price_per_night = _avg_price(hotels, destination, category, "price_per_night")
    rooms = rooms_required(travelers)
    total = price_per_night * rooms * days
    return round(total, 2), {
        "price_per_night": round(price_per_night, 2),
        "rooms": rooms,
    }


def calculate_food_cost(destination: str, days: int, travelers: int, style: str):
    restaurants = load_csv("restaurants.csv")
    category = STYLE_TO_CATEGORY[style]
    avg_per_meal = _avg_price(restaurants, destination, category, "avg_price_per_person")
    total = avg_per_meal * MEALS_PER_DAY * travelers * days
    return round(total, 2), {"avg_price_per_meal": round(avg_per_meal, 2)}


def calculate_transport_cost(destination: str, days: int, travelers: int, style: str):
    fuel = load_csv("fuel.csv")
    category = STYLE_TO_CATEGORY[style]
    price_per_day = _avg_price(fuel, destination, category, "price_per_day")
    # Luxury/Standard transport is usually priced per vehicle (covers ~4 people),
    # Budget transport (bus/shared auto) is priced per person.
    if category == "Budget":
        total = price_per_day * travelers * days
    else:
        vehicles = max(1, -(-travelers // 4))  # ceil division, 1 vehicle per 4 people
        total = price_per_day * vehicles * days
    return round(total, 2), {"price_per_day": round(price_per_day, 2)}


def calculate_attractions_cost(destination: str, days: int, travelers: int, style: str):
    tourism = load_csv("tourism.csv")
    dest_rows = tourism[tourism["destination"].str.lower() == destination.lower()]
    if dest_rows.empty:
        raise ValueError(f"No tourism data for destination '{destination}'")

    # Attractions visited per day scales mildly with travel style
    attractions_per_day = {"Budget": 1, "Standard": 2, "Luxury": 2}[style]
    n_attractions = min(len(dest_rows), attractions_per_day * days)
    # Prefer paid attractions for Standard/Luxury (richer experience), mix for Budget
    if style == "Budget":
        chosen = dest_rows.sort_values("entry_fee").head(n_attractions)
    else:
        chosen = dest_rows.sample(n=n_attractions, random_state=42) if n_attractions <= len(dest_rows) else dest_rows

    total_fee_per_person = float(chosen["entry_fee"].sum())
    total = total_fee_per_person * travelers
    return round(total, 2), {"attractions_included": chosen["attraction_name"].tolist()}


def calculate_shopping_cost(subtotal: float, style: str):
    pct = SHOPPING_PCT[style]
    total = subtotal * pct
    return round(total, 2)


def calculate_emergency_buffer(subtotal: float):
    return round(subtotal * EMERGENCY_PCT, 2)


def build_daily_breakdown(total_cost: float, days: int):
    """
    Distribute total cost across days with light, deterministic day-to-day variance
    (arrival/departure days are usually cheaper - less activity time).
    """
    if days <= 0:
        return []
    random.seed(days * 7 + int(total_cost) % 97)  # deterministic per input
    base = total_cost / days
    weights = []
    for i in range(days):
        if i == 0 or i == days - 1:
            w = random.uniform(0.85, 0.95)  # travel days: lighter spend
        else:
            w = random.uniform(0.95, 1.15)
        weights.append(w)
    weight_sum = sum(weights)
    daily = [{"day": f"Day {i+1}", "amount": round(base * (w / weight_sum) * days, 2)}
             for i, w in enumerate(weights)]
    # Correct rounding drift so totals match exactly
    drift = round(total_cost - sum(d["amount"] for d in daily), 2)
    daily[-1]["amount"] = round(daily[-1]["amount"] + drift, 2)
    return daily


def calculate_full_budget(destination: str, days: int, travelers: int, budget: float, travel_style: str):
    """
    Main entry point. Returns the full breakdown, summary, and daily chart data.
    """
    if travel_style not in STYLE_TO_CATEGORY:
        raise ValueError(f"Invalid travel_style '{travel_style}'. Use Budget, Standard, or Luxury.")

    hotel_cost, hotel_meta = calculate_hotel_cost(destination, days, travelers, travel_style)
    food_cost, food_meta = calculate_food_cost(destination, days, travelers, travel_style)
    transport_cost, transport_meta = calculate_transport_cost(destination, days, travelers, travel_style)
    attractions_cost, attractions_meta = calculate_attractions_cost(destination, days, travelers, travel_style)

    core_subtotal = hotel_cost + food_cost + transport_cost + attractions_cost
    shopping_cost = calculate_shopping_cost(core_subtotal, travel_style)
    pre_emergency_subtotal = core_subtotal + shopping_cost
    emergency_cost = calculate_emergency_buffer(pre_emergency_subtotal)

    total_cost = round(pre_emergency_subtotal + emergency_cost, 2)
    remaining = round(budget - total_cost, 2)

    breakdown = {
        "hotel": hotel_cost,
        "food": food_cost,
        "transport": transport_cost,
        "attractions": attractions_cost,
        "shopping": shopping_cost,
        "emergency": emergency_cost,
    }

    daily_breakdown = build_daily_breakdown(total_cost, days)

    return {
        "destination": destination,
        "days": days,
        "travelers": travelers,
        "travel_style": travel_style,
        "budget": budget,
        "breakdown": breakdown,
        "total_estimated_cost": total_cost,
        "remaining": remaining,
        "is_over_budget": total_cost > budget,
        "daily_breakdown": daily_breakdown,
        "meta": {
            "hotel": hotel_meta,
            "food": food_meta,
            "transport": transport_meta,
            "attractions": attractions_meta,
        },
    }
