from planner.scorer import score_option
from utils.helpers import minutes_to_hm, add_minutes_to_time

def optimize_and_recommend(options: list, preference: str, traffic: str, budget: float, dep_time: str) -> dict:
    scored = []
    for opt in options:
        s = score_option(opt, options, preference, traffic)
        scored.append({**opt, "score": s})

    scored.sort(key=lambda x: x["score"], reverse=True)
    best = scored[0]

    reasons = []
    if best["duration"] == min(o["duration"] for o in options):
        reasons.append("Fastest available route")
    if best["cost"] <= budget * 0.6:
        reasons.append("Well within your budget")
    elif best["cost"] <= budget:
        reasons.append("Within your budget")
    if best["transfers"] == 0:
        reasons.append("No transfers required")
    elif best["transfers"] == min(o["transfers"] for o in options):
        reasons.append("Fewest transfers")
    if best["eco_friendly"] and preference == "eco":
        reasons.append("Eco-friendly transport")
    if traffic == "light":
        reasons.append("Light traffic conditions")
    if not reasons:
        reasons.append(f"Best match for your '{preference}' preference")

    return {
        "recommended_mode": best["mode"],
        "travel_time": minutes_to_hm(best["duration"]),
        "estimated_cost": best["cost"],
        "distance": f"{best['distance']} km",
        "arrival": add_minutes_to_time(dep_time, best["duration"]),
        "score": best["score"],
        "reason": reasons,
        "all_options": scored
    }
