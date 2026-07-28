from config import PREFERENCE_WEIGHTS, ECO_MODES

def score_option(opt: dict, all_options: list, preference: str, traffic: str) -> float:
    weights = PREFERENCE_WEIGHTS.get(preference, PREFERENCE_WEIGHTS["fastest"])

    times = [o["duration"] for o in all_options]
    costs = [o["cost"] for o in all_options]
    max_t, min_t = max(times), min(times)
    max_c, min_c = max(costs), min(costs)

    t_score = 1 - (opt["duration"] - min_t) / (max_t - min_t + 1)
    c_score = 1 - (opt["cost"] - min_c) / (max_c - min_c + 1)
    tr_score = 1 / (opt["transfers"] + 1)
    traffic_score = {"light": 1.0, "moderate": 0.6, "heavy": 0.2}.get(traffic, 0.7)

    score = (
        weights.get("time", 0) * t_score +
        weights.get("cost", 0) * c_score +
        weights.get("transfers", 0) * tr_score +
        weights.get("traffic", 0) * traffic_score
    )

    if preference == "eco" and opt["eco_friendly"]:
        score += weights.get("eco_bonus", 0)
    if preference == "scenic" and opt["scenic"]:
        score += weights.get("scenic_bonus", 0)
    if preference == "eco" and not opt["eco_friendly"]:
        score *= 0.5

    return round(score * 100, 2)
