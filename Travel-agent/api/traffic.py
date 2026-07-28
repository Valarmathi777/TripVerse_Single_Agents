import random

def get_traffic_level(lat: float, lon: float) -> str:
    # Mapbox/HERE free tiers are very limited; simulate with slight randomness
    # Replace with real API call if key available
    levels = ["light", "moderate", "heavy"]
    weights = [0.5, 0.35, 0.15]
    return random.choices(levels, weights=weights)[0]

TRAFFIC_MULTIPLIER = {"light": 1.0, "moderate": 1.25, "heavy": 1.6}
