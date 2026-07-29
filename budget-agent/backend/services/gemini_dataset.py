"""
services/gemini_dataset.py
Responsible for calling Gemini to fetch travel details for destinations not present
in the local CSV files, converting the prices to INR, and appending them to the
respective CSV files. It also maps destinations to their local currencies and exchange rates.
"""
import json
import os
import re
from pathlib import Path
import pandas as pd
import httpx
from config import settings
from utils.helpers import load_csv

CURRENCY_MAP_PATH = settings.DATASETS_DIR / "currency_map.json"

PROMPT_TEMPLATE = """
Generate realistic, high-quality travel expense data for the destination "{destination}".
The output MUST be a single, valid JSON object containing realistic prices in the local currency of that destination.
You must also provide the currency code (e.g. USD, EUR, JPY, GBP), the currency symbol (e.g. $, €, ¥, £), and the current approximate exchange rate to Indian Rupee (INR) (e.g., 1 USD = 83.5 INR, so rate_to_inr would be 83.5).

The JSON output must follow this exact structure:
{{
  "currency_code": "USD",
  "currency_symbol": "$",
  "rate_to_inr": 83.5,
  "hotels": [
    {{
      "hotel_name": "Hotel Name",
      "category": "Budget" | "Standard" | "Luxury",
      "price_per_night": 120.0,
      "rating": 4.2,
      "max_occupancy": 2
    }}
  ],
  "restaurants": [
    {{
      "restaurant_name": "Restaurant Name",
      "category": "Budget" | "Standard" | "Luxury",
      "cuisine": "Cuisine Type",
      "avg_price_per_person": 25.0,
      "meal_type": "breakfast" | "lunch" | "dinner" | "snacks"
    }}
  ],
  "tourism": [
    {{
      "attraction_name": "Attraction Name",
      "entry_fee": 15.0,
      "type": "free" | "paid",
      "recommended_hours": 2
    }}
  ],
  "fuel": [
    {{
      "transport_mode": "Transport Mode",
      "category": "Budget" | "Standard" | "Luxury",
      "price_per_day": 45.0,
      "fuel_price_per_litre": 1.15
    }}
  ]
}}
Ensure that:
1. You provide at least 2 hotels for each category (Budget, Standard, Luxury) - total 6+ hotels.
2. You provide at least 2 restaurants for each category (Budget, Standard, Luxury) - total 6+ restaurants, covering different meal types.
3. You provide at least 5 popular tourist attractions (some free, some paid).
4. You provide transport modes: Budget (e.g., Local Bus, Shared Auto/Transit), Standard (e.g., Private Taxi, Rental Car), Luxury (e.g., Private Chauffeur, Premium Cab) with price per day and the fuel price per litre in the local region.
5. All price values under "hotels", "restaurants", "tourism", and "fuel" MUST be in the LOCAL CURRENCY of the destination (e.g. if Paris, write prices in Euros; if Tokyo, write in Japanese Yen). Do NOT write them in INR in these tables - the app will handle the conversion using "rate_to_inr".
6. Return ONLY the raw JSON block. Do not include markdown code block formatting (like ```json ... ```), just start with {{ and end with }}.
"""

def load_currency_map() -> dict:
    """Load the destination-to-currency mapping from file."""
    if not CURRENCY_MAP_PATH.exists():
        # Default map for preloaded Indian destinations
        return {}
    try:
        with open(CURRENCY_MAP_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_currency_map(data: dict):
    """Save the destination-to-currency mapping to file."""
    try:
        CURRENCY_MAP_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(CURRENCY_MAP_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[currency_map] Error saving map: {e}")

def get_destination_currency(destination: str) -> dict:
    """Return currency info for destination, default to INR if local/not found."""
    cmap = load_currency_map()
    # Case-insensitive lookup
    for dest, info in cmap.items():
        if dest.lower() == destination.lower():
            return info
    # Default to INR
    return {
        "currency_code": "INR",
        "currency_symbol": "₹",
        "rate_to_inr": 1.0
    }

def ensure_destination_data(destination: str) -> bool:
    """
    Checks if a destination is in the local datasets.
    If not, calls Gemini to generate the data, converts prices to INR,
    appends them to the CSVs, and saves the currency info.
    Returns True if data was fetched/existed, False if failed.
    """
    if not destination:
        return False
    destination = destination.strip()
    # 1. Check if hotels.csv has this destination
    try:
        df_hotels = load_csv("hotels.csv")
        exists = not df_hotels[df_hotels["destination"].str.lower() == destination.lower()].empty
        if exists:
            return True
    except Exception:
        pass

    # 2. Call Gemini to generate data
    if not settings.GEMINI_ENABLED:
        print("[gemini_dataset] Gemini API key not configured. Cannot generate dynamic dataset.")
        return False
    print(f"[gemini_dataset] Destination '{destination}' not found in local CSV. Fetching via Gemini...")
    prompt = PROMPT_TEMPLATE.format(destination=destination)
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{settings.GEMINI_MODEL}:generateContent?key={settings.GEMINI_API_KEY}"
    )
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            raw_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            # Clean JSON markdown if present
            cleaned = re.sub(r"^```json\s*", "", raw_text)
            cleaned = re.sub(r"\s*```$", "", cleaned)
            cleaned = cleaned.strip()
            parsed = json.loads(cleaned)

            # Extract currency info
            currency_code = parsed.get("currency_code", "INR").upper()
            currency_symbol = parsed.get("currency_symbol", "₹")
            rate_to_inr = float(parsed.get("rate_to_inr", 1.0))

            # Store in currency map
            cmap = load_currency_map()
            # Save using capitalized title for standard display
            capitalized_dest = destination.title()
            cmap[capitalized_dest] = {
                "currency_code": currency_code,
                "currency_symbol": currency_symbol,
                "rate_to_inr": rate_to_inr
            }
            save_currency_map(cmap)

            # Parse and append Hotels (converted to INR)
            hotels_list = []
            for h in parsed.get("hotels", []):
                hotels_list.append({
                    "destination": capitalized_dest,
                    "hotel_name": h.get("hotel_name"),
                    "category": h.get("category"),
                    "price_per_night": round(float(h.get("price_per_night", 0)) * rate_to_inr, 2),
                    "rating": float(h.get("rating", 4.0)),
                    "max_occupancy": int(h.get("max_occupancy", 2))
                })
            
            # Parse and append Restaurants (converted to INR)
            restaurants_list = []
            for r in parsed.get("restaurants", []):
                restaurants_list.append({
                    "destination": capitalized_dest,
                    "restaurant_name": r.get("restaurant_name"),
                    "category": r.get("category"),
                    "cuisine": r.get("cuisine", "Local"),
                    "avg_price_per_person": round(float(r.get("avg_price_per_person", 0)) * rate_to_inr, 2),
                    "meal_type": r.get("meal_type")
                })

            # Parse and append Tourism (converted to INR)
            tourism_list = []
            for t in parsed.get("tourism", []):
                tourism_list.append({
                    "destination": capitalized_dest,
                    "attraction_name": t.get("attraction_name"),
                    "entry_fee": round(float(t.get("entry_fee", 0)) * rate_to_inr, 2),
                    "type": t.get("type", "free"),
                    "recommended_hours": float(t.get("recommended_hours", 2))
                })

            # Parse and append Fuel/Transport (converted to INR)
            fuel_list = []
            for f in parsed.get("fuel", []):
                fuel_list.append({
                    "destination": capitalized_dest,
                    "transport_mode": f.get("transport_mode"),
                    "category": f.get("category"),
                    "price_per_day": round(float(f.get("price_per_day", 0)) * rate_to_inr, 2),
                    "fuel_price_per_litre": round(float(f.get("fuel_price_per_litre", 0)) * rate_to_inr, 2)
                })

            # Append to files
            _append_to_csv("hotels.csv", hotels_list)
            _append_to_csv("restaurants.csv", restaurants_list)
            _append_to_csv("tourism.csv", tourism_list)
            _append_to_csv("fuel.csv", fuel_list)

            # Clear pandas load_csv lru cache so it re-reads updated CSVs
            load_csv.cache_clear()
            print(f"[gemini_dataset] Successfully loaded and cached dynamic data for '{capitalized_dest}'!")
            return True
    except Exception as e:
        print(f"[gemini_dataset] Failed to fetch dynamic data for '{destination}': {e}")
        try:
            print(f"[gemini_dataset] Falling back to local mockup generation for '{destination}'...")
            return generate_mockup_destination_data(destination)
        except Exception as fe:
            print(f"[gemini_dataset] Mockup fallback also failed: {fe}")
            return False

def _append_to_csv(filename: str, rows: list):
    if not rows:
        return
    csv_path = settings.DATASETS_DIR / filename
    df_new = pd.DataFrame(rows)
    if csv_path.exists():
        df_new.to_csv(csv_path, mode="a", header=False, index=False, encoding="utf-8")
    else:
        df_new.to_csv(csv_path, mode="w", header=True, index=False, encoding="utf-8")

def normalize_destination_casing(destination: str) -> str:
    """Finds the stored casing of the destination in the CSV, defaults to title case."""
    if not destination:
        return destination
    try:
        df = load_csv("hotels.csv")
        matches = df[df["destination"].str.lower() == destination.lower()]["destination"].unique()
        if len(matches) > 0:
            return str(matches[0])
    except Exception:
        pass
    return destination.strip().title()

def generate_mockup_destination_data(destination: str) -> bool:
    """
    Generates a realistic mockup dataset locally for a destination
    if the Gemini API is offline or rate-limited.
    """
    capitalized_dest = destination.title()
    
    # 1. Determine currency
    domestic_keywords = ["goa", "ooty", "coorg", "darjeeling", "shimla", "manali", "munnar", "jaipur", "udaipur", "agra", "mumbai", "delhi", "bangalore", "bengaluru", "chennai", "kolkata", "hyderabad", "kochi", "srinagar", "leh", "madurai", "kanyakumari", "kovalam", "hampi", "mysore", "gokarna", "amritsar", "udhagamandalam"]
    is_domestic = any(k in destination.lower() for k in domestic_keywords)
    
    if is_domestic:
        currency_code = "INR"
        currency_symbol = "₹"
        rate_to_inr = 1.0
    else:
        currency_code = "USD"
        currency_symbol = "$"
        rate_to_inr = 83.5

    # Save to currency map
    try:
        cmap = load_currency_map()
        cmap[capitalized_dest] = {
            "currency_code": currency_code,
            "currency_symbol": currency_symbol,
            "rate_to_inr": rate_to_inr
        }
        save_currency_map(cmap)
    except Exception:
        pass

    # Mock hotels
    hotels_list = [
        {"destination": capitalized_dest, "hotel_name": f"Budget Stay {capitalized_dest}", "category": "Budget", "price_per_night": round(1500 / rate_to_inr, 2), "rating": 4.0, "max_occupancy": 2},
        {"destination": capitalized_dest, "hotel_name": f"Backpackers Inn {capitalized_dest}", "category": "Budget", "price_per_night": round(1200 / rate_to_inr, 2), "rating": 3.8, "max_occupancy": 2},
        {"destination": capitalized_dest, "hotel_name": f"Standard Comfort {capitalized_dest}", "category": "Standard", "price_per_night": round(4000 / rate_to_inr, 2), "rating": 4.2, "max_occupancy": 2},
        {"destination": capitalized_dest, "hotel_name": f"Grand Plaza {capitalized_dest}", "category": "Standard", "price_per_night": round(5000 / rate_to_inr, 2), "rating": 4.1, "max_occupancy": 2},
        {"destination": capitalized_dest, "hotel_name": f"Royal Orchid Resort {capitalized_dest}", "category": "Luxury", "price_per_night": round(12000 / rate_to_inr, 2), "rating": 4.7, "max_occupancy": 2},
        {"destination": capitalized_dest, "hotel_name": f"The Taj Palace {capitalized_dest}", "category": "Luxury", "price_per_night": round(18000 / rate_to_inr, 2), "rating": 4.9, "max_occupancy": 2},
    ]

    # Mock restaurants
    restaurants_list = [
        {"destination": capitalized_dest, "restaurant_name": f"Local Diner {capitalized_dest}", "category": "Budget", "cuisine": "Local", "avg_price_per_person": round(250 / rate_to_inr, 2), "meal_type": "lunch"},
        {"destination": capitalized_dest, "restaurant_name": f"Street Eats {capitalized_dest}", "category": "Budget", "cuisine": "Street Food", "avg_price_per_person": round(150 / rate_to_inr, 2), "meal_type": "snacks"},
        {"destination": capitalized_dest, "restaurant_name": f"Bistro {capitalized_dest}", "category": "Standard", "cuisine": "Multi-cuisine", "avg_price_per_person": round(750 / rate_to_inr, 2), "meal_type": "dinner"},
        {"destination": capitalized_dest, "restaurant_name": f"Cafe Cozy {capitalized_dest}", "category": "Standard", "cuisine": "Cafe", "avg_price_per_person": round(400 / rate_to_inr, 2), "meal_type": "breakfast"},
        {"destination": capitalized_dest, "restaurant_name": f"Fine Dine Luxury {capitalized_dest}", "category": "Luxury", "cuisine": "Gourmet", "avg_price_per_person": round(2500 / rate_to_inr, 2), "meal_type": "dinner"},
        {"destination": capitalized_dest, "restaurant_name": f"Sky Lounge {capitalized_dest}", "category": "Luxury", "cuisine": "Fusion", "avg_price_per_person": round(3000 / rate_to_inr, 2), "meal_type": "dinner"},
    ]

    # Mock attractions
    tourism_list = [
        {"destination": capitalized_dest, "attraction_name": f"{capitalized_dest} City Center", "entry_fee": 0.0, "type": "free", "recommended_hours": 2.0},
        {"destination": capitalized_dest, "attraction_name": f"Central Park {capitalized_dest}", "entry_fee": 0.0, "type": "free", "recommended_hours": 1.5},
        {"destination": capitalized_dest, "attraction_name": f"National Museum of {capitalized_dest}", "entry_fee": round(250 / rate_to_inr, 2), "type": "paid", "recommended_hours": 3.0},
        {"destination": capitalized_dest, "attraction_name": f"Heritage Temple & Palace", "entry_fee": round(500 / rate_to_inr, 2), "type": "paid", "recommended_hours": 2.5},
        {"destination": capitalized_dest, "attraction_name": f"Panoramic Viewpoint", "entry_fee": round(100 / rate_to_inr, 2), "type": "paid", "recommended_hours": 1.0},
    ]

    # Mock fuel/transport
    fuel_list = [
        {"destination": capitalized_dest, "transport_mode": "Local Bus & Metro", "category": "Budget", "price_per_day": round(150 / rate_to_inr, 2), "fuel_price_per_litre": round(100 / rate_to_inr, 2)},
        {"destination": capitalized_dest, "transport_mode": "Rental Scooter/Auto", "category": "Standard", "price_per_day": round(600 / rate_to_inr, 2), "fuel_price_per_litre": round(100 / rate_to_inr, 2)},
        {"destination": capitalized_dest, "transport_mode": "Private Sedan Cab", "category": "Standard", "price_per_day": round(2200 / rate_to_inr, 2), "fuel_price_per_litre": round(100 / rate_to_inr, 2)},
        {"destination": capitalized_dest, "transport_mode": "Luxury Chauffeur SUV", "category": "Luxury", "price_per_day": round(6000 / rate_to_inr, 2), "fuel_price_per_litre": round(100 / rate_to_inr, 2)},
    ]

    # Convert to INR for CSV files
    for h in hotels_list:
        h["price_per_night"] = round(h["price_per_night"] * rate_to_inr, 2)
    for r in restaurants_list:
        r["avg_price_per_person"] = round(r["avg_price_per_person"] * rate_to_inr, 2)
    for t in tourism_list:
        t["entry_fee"] = round(t["entry_fee"] * rate_to_inr, 2)
    for f in fuel_list:
        f["price_per_day"] = round(f["price_per_day"] * rate_to_inr, 2)
        f["fuel_price_per_litre"] = round(f["fuel_price_per_litre"] * rate_to_inr, 2)

    _append_to_csv("hotels.csv", hotels_list)
    _append_to_csv("restaurants.csv", restaurants_list)
    _append_to_csv("tourism.csv", tourism_list)
    _append_to_csv("fuel.csv", fuel_list)

    load_csv.cache_clear()
    print(f"[gemini_dataset] Successfully generated mockup local data for '{capitalized_dest}'!")
    return True